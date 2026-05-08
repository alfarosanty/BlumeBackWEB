import os
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from typing import Optional, Any
from dotenv import load_dotenv

from app.models.Presupuesto import Presupuesto

load_dotenv()

class EmailService:
    def __init__(self):
        self.smtp_server: str = os.getenv("SMTP_SERVER") or "smtp.gmail.com"
        self.smtp_port: int = int(os.getenv("SMTP_PORT") or 587)
        self.sender_email: str = os.getenv("EMAIL_USER") or ""
        self.sender_password: str = os.getenv("EMAIL_PASS") or ""
        self.sender_name: str = os.getenv("EMAIL_NAME") or "Blume"

    def enviar_notificacion_presupuesto(self, email_destino: str, presupuesto: Presupuesto, pdf_content: Optional[bytes] = None):
        if not self.sender_email or not self.sender_password:
            print("Error: Credenciales de email no configuradas.")
            return False

        estado_actual = presupuesto.estado.value if hasattr(presupuesto.estado, 'value') else str(presupuesto.estado)
        
        config_estados = {
            "creado": {
                "asunto": f"Solicitud de Presupuesto #{presupuesto.numero_presupuesto_cliente} - Recibida",
                "mensaje": "Hemos recibido tu solicitud. Estamos validando el stock de los artículos."
            },
            "validado": {
                "asunto": f"Presupuesto Validado #{presupuesto.numero_presupuesto_cliente}",
                "mensaje": "Tu presupuesto ha sido validado correctamente. Adjunto encontrarás el detalle final."
            },
            "eliminado": {
                "asunto": f"Presupuesto Cancelado #{presupuesto.numero_presupuesto_cliente}",
                "mensaje": "Tu presupuesto ha sido cancelado. Si tenés dudas, ponete en contacto con nosotros."
            }
        }

        config = config_estados.get(estado_actual, config_estados["creado"])

        msg = EmailMessage()
        msg['Subject'] = config["asunto"]
        msg['From'] = formataddr((self.sender_name, self.sender_email))
        msg['To'] = email_destino
        
        cuerpo = (
            f"Hola {presupuesto.cliente.razon_social if presupuesto.cliente else ''},\n\n"
            f"{config['mensaje']}\n\n"
            f"Número de Presupuesto: #{presupuesto.numero_presupuesto_cliente}\n"
            f"Fecha: {presupuesto.fecha_creacion.strftime('%d/%m/%Y')}\n\n"
            f"Saludos,\n"
            f"Equipo de {self.sender_name}"
        )
        msg.set_content(cuerpo)

        if pdf_content and estado_actual != "eliminado":
            msg.add_attachment(
                pdf_content,
                maintype='application',
                subtype='pdf',
                filename=f"Presupuesto_{presupuesto.numero_presupuesto_cliente}.pdf"
            )

        try:
            if self.smtp_port == 465:
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                    server.login(self.sender_email, self.sender_password)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.sender_email, self.sender_password)
                    server.send_message(msg)
            
            print(f"--- Mail enviado con éxito para Presupuesto ID: {presupuesto.id} ---")
            return True
        except Exception as e:
            print(f"Error enviando email: {e}")
            return False
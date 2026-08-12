"""
==========================================================
Face3D Studio AI

Registration Loader

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from source.reconstruction.registration.template_registration import (
    TemplateRegistration,
)


class RegistrationLoader:
    """
    Carica la registrazione di un template.

    Versione 1.0

    Restituisce una registrazione vuota.
    """

    @staticmethod
    def load(
        template_name: str,
    ) -> TemplateRegistration:
        """
        Restituisce la registrazione del
        template richiesto.
        """

        return TemplateRegistration(
            template_name=template_name
        )
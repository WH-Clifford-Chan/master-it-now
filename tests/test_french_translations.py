import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app


def test_french_locale_returns_translated_strings():
    app = create_app()

    with app.test_request_context('/'):
        from flask import session
        from flask_babel import gettext as _

        session['lang'] = 'fr'

        assert _('Login') == 'Se connecter'
        assert _('Create Account') == 'Créer un compte'
        assert _('Flashcards') == 'Fiches de révision'
        assert _('Settings') == 'Paramètres'
        assert _('Back') == 'Retour'

from breeze.uimodules import BaseModal


class SignInModal(BaseModal):
    template = 'core/auth/sign-in-modal.html'


class RegisterModal(SignInModal):
    template = 'core/auth/register-modal.html'

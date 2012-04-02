"""
API views not coupled to models.
"""
from djangorestframework.views import View

from lizard_registration.models import SessionContextStore
from lizard_registration.models import UserContextStore


class ContextView(View):
    """
        Get user context
    """
    def get(self, request):

        user = request.user
        successful = True
        context = ''

        if user.iprangelogin_set.all().count() > 0:
            session_key = request.session.session_key
            try:
                context_store = user.sessioncontextstore.get(
                    session_key=session_key)
                context = context_store.context
            except SessionContextStore.DoesNotExist:
                successful = False
        else:
            try:
                context = user.usercontextstore.context
            except UserContextStore.DoesNotExist:
                successful = False

        return {
            "data": context,
            "successful": successful
            }

    def post(self, request):

        user = request.user
        context = self.CONTENT.get('context', None)

        if user.iprangelogin_set.all().count() > 0:
            #context of public account are stored based on session_key
            session_key = request.session.session_key
            context_store, new = user.sessioncontextstore_set.get_or_create(
                session_key=session_key)
            context_store.context = context
            context_store.save()
        else:
            context_store, new = UserContextStore.objects.get_or_create(
                user=user)
            context_store.context = context
            context_store.save()

        return {
            "successful": True
            }

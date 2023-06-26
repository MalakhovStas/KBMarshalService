from utils.time_utils import get_time_left
from django.views.generic import DetailView, TemplateView


class HomePageView(TemplateView):
    """ Отображение главной страницы сайта """
    template_name = "home.j2"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        days, hours, minutes, seconds = get_time_left()
        # context['banners'] = Banner.objects.get_active_banners()
        # context['top_products'] = get_top_products()
        # context["offer_of_the_day"] = get_offer_of_the_day()
        context["days"] = days
        context["hours"] = hours
        context["minutes"] = minutes
        context["seconds"] = seconds
        # print(self.request.user)
        # print(self.request.user.user_permissions)
        # print(self.request.user.groups)
        # print(self.request.user.groups.filter(name__in=['users']).exists())
        # context["hot_deals"] = hot_deals()
        # context["limited_edition_products"] = limited_edition_products()
        return context


class PrivacyPolicyPageView(TemplateView):
    """ Отображение страницы политики конфиденциальности сайта """
    template_name = "/includes/footer/privacy_policy.j2"

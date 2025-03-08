from django_filters import rest_framework as filters
from django.utils import timezone
from .models import Poll

class PollFilter(filters.FilterSet):
    """
    Filter class for Polls
    """
    title = filters.CharFilter(lookup_expr='icontains')
    created_by = filters.NumberFilter(field_name='created_by__id')
    is_ongoing = filters.BooleanFilter(method='filter_ongoing')
    
    class Meta:
        model = Poll
        fields = ['title', 'created_by']
    
    def filter_ongoing(self, queryset, name, value):
        if value:
            return queryset.filter(expire_date__gte=timezone.now())
        return queryset.filter(expire_date__lt=timezone.now())
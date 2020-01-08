from django import forms


class FilterWidget(forms.widgets.CheckboxSelectMultiple):
    template_name = 'datasets/filter.html'
    option_template_name = "datasets/filter_option.html"

    def __init__(self, group_label, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._group_label = group_label

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['group_label'] = self._group_label
        return context


class RequestAccessForm(forms.Form):
    email = forms.CharField(widget=forms.TextInput, required=True)
    goal = forms.CharField(widget=forms.Textarea, required=True)
    justification = forms.CharField(widget=forms.Textarea, required=True)


class EligibilityCriteriaForm(forms.Form):
    meet_criteria = forms.TypedChoiceField(
        widget=forms.RadioSelect,
        coerce=lambda x: True if x == 'yes' else False,
        choices=(('no', 'No'), ('yes', 'Yes')),
    )

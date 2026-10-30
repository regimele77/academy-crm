from django import forms

from course.models import CourseGroupModel, CourseModel


class CourseForm(forms.ModelForm):
    class Meta:
        model = CourseModel
        fields = ['name', 'description', 'price']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g. Python Fundamentals',
                'autocomplete': 'off',
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Optional short description of the course',
            }),
            'price': forms.NumberInput(attrs={
                'min': '0',
                'step': '0.01',
                'placeholder': '0.00',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = 'Course name'
        self.fields['description'].required = False
        self.fields['price'].label = 'Price'


class CourseGroupForm(forms.ModelForm):
    class Meta:
        model = CourseGroupModel
        fields = ['name', 'course', 'start_date', 'end_date']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g. Spring 2026 cohort',
                'autocomplete': 'off',
            }),
            'start_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'end_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }

    def __init__(self, *args, course_queryset=None, lock_course=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = 'Group name'
        self.fields['course'].label = 'Course'
        self.fields['start_date'].label = 'Start date'
        self.fields['end_date'].label = 'End date'
        self.fields['start_date'].input_formats = ['%Y-%m-%d']
        self.fields['end_date'].input_formats = ['%Y-%m-%d']
        if course_queryset is not None:
            self.fields['course'].queryset = course_queryset.order_by('name')
        self.fields['course'].empty_label = 'Select a course'
        if lock_course is not None:
            self.fields['course'].queryset = CourseModel.objects.filter(pk=lock_course.pk)
            self.fields['course'].initial = lock_course.pk
            self.fields['course'].widget = forms.HiddenInput()

    def clean(self):
        cleaned = super().clean()
        start_date = cleaned.get('start_date')
        end_date = cleaned.get('end_date')
        if start_date and end_date and end_date < start_date:
            self.add_error('end_date', 'End date must be on or after the start date.')
        return cleaned

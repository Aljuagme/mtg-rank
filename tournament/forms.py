from django import forms

class ListPlayersForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ListPlayersForm, self).__init__(*args, **kwargs)
        for i in range(1, 9):
            self.fields[f'player{i}'] = forms.CharField(
                min_length=3,
                max_length=20,
                widget=forms.TextInput(
                    attrs={'class': 'form-control', 'placeholder': f'Player{i}'}
                )
            )


    def clean(self):
        cleaned_data = super().clean()
        players = [cleaned_data.get(f"player{i}") for i in range(1, 9)]

        player_names = [name for name in players if name]

        if len(player_names) != len(set(player_names)):
            raise forms.ValidationError("All players must have unique names")
        for name in player_names:
            if  len(name) < 3:
                raise forms.ValidationError("Names must have at least 3 characters")
'''
Defines forms for the `data` django app
'''


import csv
import json
import os

from django import forms
from django.conf import settings

from data_upload_app import models


class UploadCsvFileForm(forms.Form):
    '''
    Form provides fields for a user to upload a csv file containing instance data, plus extra data
    to describe the file.
    '''

    abm_match_json = forms.CharField(required=True, widget=forms.Textarea)
    upload_file = forms.FileField(required=True, max_length=50, widget=forms.ClearableFileInput())

    def __del__(self):
        '''
        Custom destructor to delete the temporary file if it exists
        '''

        if self.upload_file_path:
            if os.path.exists(self.upload_file_path):
                # Delete the temp file as we're done with it
                os.remove(self.upload_file_path)

    def __init__(self, *args, **kwargs):
        '''
        Override default `__init__()` to store any uploaded files to storage for processing later
        '''

        # Default init
        super().__init__(*args, **kwargs)

        self.abm_match_dict = None
        self.upload_file_path = self.save_temporary_file()

    def clean(self):
        '''
        Override form clean to check that incoming `abm_match_json` json data references valid
        column names in the uploaded csv file
        '''

        column_names = None
        column_name_errors = []

        cleaned_data = super().clean()

        if self.abm_match_dict:
            # If we have a valid dictionary of `AbtractModel` entries, open the csv and check the
            # keys are present as column names
            with open(self.upload_file_path, 'r') as csv_file:
                reader = csv.DictReader(csv_file)
                column_names = reader.fieldnames

            # Loop through the `abm_match_dict` and check if column names exist
            for key in self.abm_match_dict.keys():
                if not key in column_names:
                    column_name_errors += ['Column name "' + key + '" does not exist in "' +
                                           os.path.basename(self.upload_file_path) + '".']

            # If we've produced any errors, add them to the `upload_file` field
            if column_name_errors:
                self.add_error('upload_file', column_name_errors)

        return cleaned_data

    def clean_abm_match_json(self):
        '''
        Override field clean to check the input abm_match_json:
         * is actually json
         * references valid `AbstractModel` entries
        '''

        abm_match_json = self.cleaned_data['abm_match_json']

        # Check the input data is actually json
        try:
            self.abm_match_dict = json.loads(abm_match_json)

        except json.JSONDecodeError as err:
            # If input data is not json, raise error
            self.add_error('abm_match_json', [err])

        # Now check if the data contains valid `AbstractModel` entries
        if self.abm_match_dict:
            # Check that the referenced `AbstractModel` ids actually exist
            if not all([models.AbstractModel.objects.filter(id=e).exists() for e in self.abm_match_dict.values()]): # pylint: disable=line-too-long
                self.add_error(
                    'abm_match_json',
                    'Data contains references to AbstractModel entries that do not exist.'
                )
                # Clear the `abm_match_dict` as the data is invalid
                self.abm_match_dict = None

        return abm_match_json


    def clean_upload_file(self):
        '''
        Override field clean to check the uploaded file is a valid csv file
        '''

        if not os.path.splitext(os.path.basename(self.upload_file_path))[1] == '.csv':
            # If extension is not csv, raise error
            self.add_error(
                'upload_file',
                '"' + os.path.basename(self.upload_file_path) + '" is not a valid csv.'
            )

        return self.cleaned_data.get('upload_file')

    def save(self):
        '''
        Method creates new `Instance` entries from the `upload_file` csv if all input data has
        been validated
        '''

        abm_ids = {}
        new_entries = []

        # First unpack the `abm_match_dict` and group column names by abm_id
        for key, value in self.abm_match_dict.items():
            # If a referenced `AbstractModel` id already exists, append the column name
            if abm_ids.get(value, None):
                abm_ids[value] =  abm_ids[value] + [key]
            else:
                abm_ids[value] = [key]

        # Now open the csv and create `Instance` entries based on row data
        with open(self.upload_file_path, 'r') as csv_file:
            reader = csv.DictReader(csv_file)

            for row in reader:
                # Loop through each abm_id in abm_ids and create instances based on the
                # `AbstractModel` referenced
                for abm_id, column_names in abm_ids.items():
                    attribute_data = {}

                    for col_name in column_names:
                        attribute_data[col_name] = row[col_name]

                    entry = models.Instance.objects.create(
                        abm=models.AbstractModel.objects.get(id=abm_id),
                        attribute=json.dumps(attribute_data)
                    )

                    # Add new entry to the list
                    new_entries += [entry]

        return new_entries

    def save_temporary_file(self):
        '''
        Method saves `upload_file` to a temporary location if it exists, and returns the full path
        of the new temporary file. If `upload_file` is not valid, returns None
        '''

        # Return None by default.
        upload_file_path = None

        upload_file = self.files.get('upload_file', None)

        # if uploaded file exists, save to temp location
        if upload_file:
            upload_file_path = os.path.join(settings.TEMP_FILES_DIR, upload_file.name)

            with open(upload_file_path, 'wb+') as destination:
                for chunk in upload_file.chunks():
                    destination.write(chunk)

        return upload_file_path

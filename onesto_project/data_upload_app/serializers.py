'''
Defines serializers for the `data` Django app

Serializers defines how a model entry should be serialized to json, and also how input json data
should be validated and saved to a new model entries
'''


from rest_framework import serializers

from data_upload_app import models


class AttributeSerializer(serializers.ModelSerializer):
    '''
    Serializer for the `Attribute` model
    '''

    attribute_name = serializers.CharField(source='name')
    value_dtype = serializers.CharField(source='dtype.__str__')

    class Meta:
        fields = ['id','attribute_name', 'value_dtype']
        model = models.Attribute

    def create(self, validated_data):
        '''
        create method creates or updates a single db entry
        '''

        # Pop out `value_dtype` to look up the entry
        input_dtype = validated_data.pop('dtype')

        # Get or create `DataType` entry first
        data_type, _ = models.DataType.objects.get_or_create(
            name=input_dtype['__str__']
        )

        # Then get or create `Attribute`
        entry, _ = models.Attribute.objects.get_or_create(dtype=data_type, **validated_data)

        return entry


class InstanceSerializer(serializers.ModelSerializer):
    '''
    Serializer for the `Instance` model
    '''

    abm = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='data:abstractmodel-detail'
    )
    item = serializers.CharField(source='abm.master_item')

    class Meta:
        fields = ['item', 'id', 'abm', 'attribute', 'measure', 'link']
        model = models.Instance


class MeasureSerializer(serializers.ModelSerializer):
    '''
    Serializer for the `Measure` model
    '''

    measure_name = serializers.CharField(source='name')
    value_dtype = serializers.CharField(source='value_dtype.__str__')

    class Meta:
        fields = ['measure_name', 'measure_type', 'unit_of_measurement', 'value_dtype',
                  'statistic_type', 'measurement_reference_time', 'measurement_precision']
        model = models.Measure

    def create(self, validated_data):
        '''
        create method creates or updates a single db entry
        '''

        # Pop out `value_dtype` to look up the entry
        input_dtype = validated_data.pop('value_dtype')

        # Get or create `DataType` entry first
        data_type, _ = models.DataType.objects.get_or_create(
            name=input_dtype['__str__']
        )

        # Then get or create `Measure`
        entry, _ = models.Measure.objects.get_or_create(value_dtype=data_type, **validated_data)

        return entry


class AMLinkSerializer(serializers.ModelSerializer):
    '''
    Serializer for the `AMLink` model
    '''

    relationship = serializers.CharField(source='relationship.__str__')

    class Meta:
        fields = ['relationship', 'instances_value_dtype', 'time_link', 'link_criteria', 'values']
        model = models.AMLink

    def create(self, validated_data):
        '''
        create method creates or updates a single db entry
        '''

        # Pop out `value_dtype` to look up the entry
        input_relationship = validated_data.pop('relationship')

        # Get or create `Relationship` entry first
        relationship, _ = models.Relationship.objects.get_or_create(
            relationship_str=input_relationship['__str__']
        )

        # Then get or create `AMLink`
        entry, _ = models.AMLink.objects.get_or_create(relationship=relationship, **validated_data)

        return entry


class AbstractModelSerializer(serializers.ModelSerializer):
    '''
    Serializer for the `AbstractModel` model
    '''

    master_item = serializers.CharField(source='master_item.__str__')
    attribute = AttributeSerializer(many=True)
    measure = MeasureSerializer(many=True)
    link = AMLinkSerializer(many=True)

    class Meta:
        fields = ('__all__')
        model = models.AbstractModel

    def create(self, validated_data):
        '''
        create method creates or updates new db entries
         * `Item` from input `master_item`
         * `Attribute`s from input `attribute` data
         * `Measure`s from input `measure` data
         * `AMLink`s from input `link` data

        It does this by using other serializers to do the work
        We always call `is_valid()` required before we call `save()`
        '''

        # Get or create `Item` entry
        item, _ = models.Item.objects.get_or_create(name=validated_data['master_item']['__str__'])

        # Call `AttributeSerializer` with the data to save to new `Attribute` entries
        attribute_serializer = AttributeSerializer(data=self.initial_data['attribute'], many=True)
        attribute_serializer.is_valid()
        attributes = attribute_serializer.save()

        # Call `MeasureSerializer` with the data to save to new `Measure` entries
        measure_serializer = MeasureSerializer(data=self.initial_data['measure'], many=True)
        measure_serializer.is_valid()
        measures = measure_serializer.save()

        # Call `AMLink` with the data to save to new `AMLink` entries
        link_serializer = AMLinkSerializer(data=self.initial_data['link'], many=True)
        link_serializer.is_valid()
        links = link_serializer.save()

        # Now create the `AbstractModel` entry with all the created relationships from above
        entry = models.AbstractModel.objects.create(master_item=item)

        for a in attributes: # pylint: disable=invalid-name
            entry.attribute.add(a)

        for m in measures: # pylint: disable=invalid-name
            entry.measure.add(m)

        for l in links: # pylint: disable=invalid-name
            entry.link.add(l)

        return entry

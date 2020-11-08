'''
Defines all database tables for the `data` django app
'''


import re

from django.db import models


class DataType(models.Model):
    '''
    Defines db table for `DataType`s
    '''

    name = models.CharField(max_length=140, unique=True) # e.g. VARCHAR, MEASURE, INT etc

    def save(self, *args, **kwargs): # pylint: disable=signature-differs
        '''
        Override default save method to set `name` field contents to upper case
        '''

        self.name = self.name.upper()

        # Call default inherited save
        super().save(*args, **kwargs)

    def __str__(self):
        '''
        Defines the return string for a `DataType` db table entry
        '''

        return self.name


class Item(models.Model):
    '''
    Defines db table for an `Item`
    '''

    name = models.CharField(max_length=140, unique=True)

    def save(self, *args, **kwargs): # pylint: disable=signature-differs
        '''
        Override default save method to set `name` field contents to title case
        '''

        self.name = self.name.capitalize()

        # Call default inherited save
        super().save(*args, **kwargs)

    def __str__(self):
        '''
        Defines the return string for an `Item` db table entry
        '''

        return self.name


class Relationship(models.Model):
    '''
    Defines db table for a `Relationship` e.g. (Book)<-[WROTE]-(Person)
    '''

    item = models.ManyToManyField(Item) # Assume this would normally be maximum of two?
    relationship_str = models.CharField(max_length=140) # e.g. (Book)<-[WROTE]-(Person)

    def save(self, *args, **kwargs): # pylint: disable=signature-differs
        '''
        Override save method to do validation on the `relationship_str`

         * create relationships to `Item` entries based on input `relationship_str`. If `Item`
           entries do not exist, create them
         * Perform some sort of validation on the string itself using a regex.
           What is the expected makeup of this string?
        '''

        # Call default save to create the entry
        super().save(*args, **kwargs)

        # Find any `Items` in the input `relationship_str`
        m = re.match(r'^\((\w+)\).+\((\w+)\)$', self.relationship_str) # pylint: disable=invalid-name

        # If we find some, get or create `Item` entries
        if m:
            item_1, _ = Item.objects.get_or_create(name=m.group(1))
            item_2, _ = Item.objects.get_or_create(name=m.group(2))

            # Add these `Item` entries to the `ManyToMany` field
            self.item.add(item_1, item_2)

    def __str__(self):
        '''
        Defines the return string for an `Relationship` db table entry
        '''

        return self.relationship_str


class Attribute(models.Model):
    '''
    Defines db table for an `Attribute`
    '''

    name = models.CharField(max_length=140, unique=True) # Is this unique?
    dtype = models.ForeignKey(DataType, on_delete=models.CASCADE)

    def __str__(self):
        '''
        Defines the return string for an `Attribute` db table entry
        '''

        return self.name


class Measure(models.Model):
    '''
    Defines db table for a `Measure`
    '''

    name = models.CharField(max_length=140)
    measure_type = models.CharField(max_length=140) # This could be limited to a choice if there
                                                    # are limited types, or `ForeignKey` to a db
                                                    # table if you want to search/filter by
                                                    # measure_type
    unit_of_measurement = models.CharField(max_length=140)
    value_dtype = models.ForeignKey(DataType, on_delete=models.CASCADE)
    statistic_type = models.CharField(max_length=140) # This could be limited to a choice if
                                                      # there are limited types, or `ForeignKey`
                                                      # to a db table if you want to search/filter
                                                      # by statistic_type
    measurement_reference_time = models.CharField(max_length=140)
    measurement_precision = models.CharField(max_length=140)

    def __str__(self):
        '''
        Defines the return string for an `Measure` db table entry
        '''

        return self.name


# It may be better to combine `AMLink` and `InstanceLink` tables into one `Link` table
# if the data looks common across both
class AMLink(models.Model):
    '''
    Defines db table for a `AMLink`
    '''

    relationship = models.ForeignKey(Relationship, on_delete=models.CASCADE)
    instances_value_dtype = models.CharField(max_length=140)
    time_link = models.BooleanField()
    link_criteria = models.CharField(max_length=140)
    values = models.CharField(max_length=140) # Could also be a json field if this is dictionary
                                              # like


class AbstractModel(models.Model):
    '''
    Defines db table for `AbstractModel`
    '''

    master_item = models.ForeignKey(Item, on_delete=models.CASCADE)
    attribute = models.ManyToManyField(Attribute)
    measure = models.ManyToManyField(Measure)
    link = models.ManyToManyField(AMLink)


# See `AMLink` above
class InstanceLink(models.Model):
    '''
    Defines db table for `InstanceLink`
    '''

    relationship = models.ForeignKey(Relationship, on_delete=models.CASCADE)
    landing_instance = models.CharField(max_length=140) # Could be a `models.UrlField` if this is
                                                        # always a url


# Need a bit more information on what a `Link` and a `IncomingInteractionLink` are
class IncomingInteractionLink(models.Model):
    '''
    Defines db table for `IncomingInteractionLink`
    '''

    relationship = models.CharField(max_length=140)
    origin_instance = models.CharField(max_length=140) # Could be a `models.UrlField` if this is
                                                       # always a url

    def __str__(self):
        '''
        Defines the return string for an `IncomingInteractionLink` db table entry
        '''

        return self.relationship


class Instance(models.Model):
    '''
    Defines db table for `Instance`
    '''

    abm = models.ForeignKey(AbstractModel, on_delete=models.CASCADE)
    attribute = models.JSONField(encoder=None)
    measure = models.JSONField(encoder=None)
    link = models.ManyToManyField(InstanceLink) # e.g. (Book)<-[WROTE]-(Person)
    iil = models.ManyToManyField(IncomingInteractionLink)


class RankingCluster(models.Model):
    '''
    Defines db table for `RankingCluster`
    '''

    master_item = models.ForeignKey(Item, on_delete=models.CASCADE)
    ranking_feature = models.CharField(max_length=140, null=True, blank=True)
    number_of_instances = models.PositiveIntegerField(null=True, blank=True)
    instances_ranking = models.CharField(max_length=140, null=True, blank=True)
    links_ranking = models.CharField(max_length=140, null=True, blank=True)

    def update(self, *args, **kwargs):
        '''
        Update entry whenever new `Instance` entries are added to the database with
        a matching `master_item`

        This will then use the `relationship` foreignkeys to update `score`,
        `number_of_instances`, `instances_ranking` and `links_ranking` fields
        '''

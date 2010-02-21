from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)

class Tag(models.Model):
    name = models.CharField(max_length=255)

    class Testing:
        defaults = {}

class Archive(models.Model):
    pass

class Article(models.Model):
    boolean = models.BooleanField()
    name = models.CharField(blank=True, max_length=255)
    date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    decimal = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=2)
    email = models.EmailField(blank=True)
    filez = models.FileField(null=True, blank=True, upload_to="articles")
    filepath = models.FilePathField(null=True, blank=True)
    floaty = models.FloatField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to="articles")
    integer = models.IntegerField(null=True, blank=True)
    ip = models.IPAddressField(null=True, blank=True)
    nullbool = models.NullBooleanField(null=True)
    slug = models.SlugField(blank=True)
    text = models.TextField(blank=True)
    time = models.TimeField(null=True, blank=True)
    url = models.URLField(blank=True)
    xml = models.XMLField(blank=True)

    category = models.ForeignKey(Category, related_name="articles", null=True)
    tags = models.ManyToManyField(Tag, related_name="articles", null=True)
    archive = models.OneToOneField(Archive, related_name="article", null=True)

    class Testing:
        pass

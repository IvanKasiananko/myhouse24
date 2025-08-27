from django.db import models


class SEO(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    keywords = models.TextField()


class Contact(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    site = models.URLField()
    location = models.CharField(max_length=255)
    address = models.CharField(
        max_length=255
    )  # исправлено: adress -> address (если встречалось)
    phone = models.CharField(max_length=255)
    email = models.EmailField()
    map = models.CharField(max_length=255)
    SEO = models.ForeignKey("pages.SEO", on_delete=models.PROTECT)


class TariffPage(models.Model):
    title = models.CharField(max_length=255)  # исправлено: charfiled -> CharField
    description = models.TextField()
    SEO = models.ForeignKey("pages.SEO", on_delete=models.PROTECT)


class ShowcasePage(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    main_image_1 = models.ImageField(upload_to="pages/showcase/")
    main_image_2 = models.ImageField(upload_to="pages/showcase/")
    main_image_3 = models.ImageField(upload_to="pages/showcase/")
    SEO = models.ForeignKey("pages.SEO", on_delete=models.PROTECT)


class ImageBlock(models.Model):
    TariffPage = models.ForeignKey("pages.TariffPage", on_delete=models.PROTECT)
    ShowcasePage = models.ForeignKey("pages.ShowcasePage", on_delete=models.PROTECT)
    image = models.ImageField(upload_to="pages/blocks/")
    caption = models.CharField(max_length=255)
    description = models.TextField()


class AboutPage(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    SEO = models.ForeignKey("pages.SEO", on_delete=models.PROTECT)


class AboutPageGallery(models.Model):
    image = models.ImageField(upload_to="pages/about/")
    section = models.CharField(max_length=255)
    AboutPage = models.ForeignKey("pages.AboutPage", on_delete=models.PROTECT)

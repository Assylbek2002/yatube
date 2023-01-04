from django.test import TestCase, Client
from .models import User, Post
from django.urls import reverse


class TestUser(TestCase):
    def setUp(self):
        self.test_user = User.objects.create(first_name='TestUser4', last_name='TestUser4', username='testuser4')
        self.test_user.set_password('testtest14')
        self.test_user.save()
        self.c = Client()
        self.c.login(username='testuser4', password='testtest14')
        with open("media/posts/CYIY7OgglyQ.jpg", 'rb') as img:
            self.c.post("/new/", data={
                "text": "Барселона попробует оспорить удаление Жорди Альбы в матче с «Эспаньолом», чтобы тот сыграл с «Атлетико».",
                "image": img})

    """После регистрации пользователя создается его персональная страница (profile)"""
    def test_profile(self):
        c = Client()
        c.login(username='testuser4', password='testtest14')
        response = c.get(f"/{self.test_user.username}/")
        self.assertEqual(response.status_code, 200)

    """Авторизованный пользователь может опубликовать пост (new)"""
    def test_add_post(self):
        post = Post.objects.filter(text__contains="Жорди")
        self.assertTrue(post.exists())

    def test_pages(self):
        post = Post.objects.filter(text__contains="Жорди")

        # После публикации поста новая запись появляется на главной странице сайта (index)
        response_main_page = self.c.get("")
        self.assertContains(response_main_page, "Жорди")

        # После публикации поста новая запись появляется на персональной странице пользователя (profile)
        response_profile_page = self.c.get(f"/{self.test_user.username}/")
        self.assertContains(response_profile_page, "оспорить")

        # После публикации поста новая запись появляется на отдельной странице поста (post)
        response_post_page = self.c.get(f"/{self.test_user.username}/{post[0].id}/")
        self.assertContains(response_post_page, "оспорить")

        # Неавторизованный посетитель не может опубликовать пост (его редиректит на страницу входа)
        unauthorized_user = Client()
        response_unauthorized = unauthorized_user.get("/new/")
        self.assertEqual(response_unauthorized.status_code, 302)
        self.assertRedirects(response_unauthorized, "/auth/login/?next=/new/")

    def test_post_page_has_image(self):
        post = Post.objects.filter(text__contains="Жорди")
        response = self.c.get(f"/{self.test_user.username}/{post[0].id}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<img')

    def test_main_page_has_image(self):
        response = self.c.get("")
        self.assertContains(response, '<img')

    def test_edit_post(self):
        post = Post.objects.filter(text__contains="Жорди")
        response = self.c.get(f"/{self.test_user.username}/{post[0].id}/edit/")
        form = response.context["form"] # get label
        data = form.initial # get dictionary
        data["text"] = "ОФИЦИАЛЬНО: Луис Суарес — игрок бразильского «Гремио»."
        data["group"] = ""
        data["image"] = ""
        response = self.c.post(f"/{self.test_user.username}/{post[0].id}/edit/", data=data, follow=True)
        self.assertContains(response, "Луис")

    def test_upload_correct_data(self):
        with open("media/posts/gradus.txt", 'rb') as file:
            data = {"text": "Этот год мы никогда не забудем 🤍🏆", "image": file}
            response = self.c.post("/new/", data=data)
        self.assertContains(response, "Upload a valid image. The file you uploaded was either not an image or a corrupted image.")

    def test_cache(self):
        response = self.c.get(reverse('index'))
        self.c.post("/new/", data={
            "text": "📰 Standard Sport: «Барселона» имеет все шансы подписать Н'Голо Канте, если тот не продлит контракт с «Челси»."})
        self.assertNotContains(response, "Канте")

    def tearDown(self):
        self.test_user.delete()




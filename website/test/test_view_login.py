#!/usr/bin/env python
# -*- coding: utf-8 -*-
from website.models import User
from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from django.urls import reverse


setup_test_environment()


class LoginViewTests(TestCase):

    def setUp(self):
        self.username = "i.stravinsky"
        self.password = "Стравинский"

        User.objects.create_user(
            username=self.username,
            password=self.password)

        self.client = Client()

    def test_successful_login(self):
        """Client can successfully log in and is redirected to overview page"""
        post_data = {"username": self.username, "password": self.password}

        response = self.client.post(reverse("login"), post_data)

        self.assertEqual(302, response.status_code)
        self.assertEqual(reverse("overview"), response.url)

    def test_no_login_for_wrong_username(self):
        """Client can not be log in with a wrong password"""
        post_data = {"username": self.username, "password": "admin"}

        response = self.client.post(reverse("login"), post_data)

        self.assertEqual(200, response.status_code)
        self.assertEqual(False, response.context["form"].is_valid())

    def test_no_login_for_wrong_password(self):
        """Client can not log in with a wrong username"""
        post_data = {"username": "i.dont.exist", "password": self.password}

        response = self.client.post(reverse("login"), post_data)

        self.assertEqual(200, response.status_code)
        self.assertEqual(False, response.context["form"].is_valid())

    def test_no_login_for_wrong_credentials(self):
        """Client can not log in with a wrong username"""
        post_data = {"username": "i.dont.exist", "password": "admin"}

        response = self.client.post(reverse("login"), post_data)

        self.assertEqual(200, response.status_code)
        self.assertEqual(False, response.context["form"].is_valid())

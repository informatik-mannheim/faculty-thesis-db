#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.urls import reverse

from website.models import Thesis
from website.test.test import LoggedInTestCase, ThesisStub

from datetime import timedelta


class ViewTestHandin(LoggedInTestCase):

    def test_default_values_are_set_correctly(self):
        """Hand In Date should default to deadline of thesis"""
        thesis = ThesisStub.applied(self.supervisor)
        thesis.restriction_note = True
        thesis.save()

        response = self.client.get(
            reverse('handin', args=[thesis.surrogate_key]))

        context = response.context
        form = context["form"]

        self.assertEqual(200, response.status_code)
        self.assertEqual(context["thesis"], thesis)
        self.assertEqual(form["new_title"].value(), thesis.title)
        self.assertEqual(form["handed_in_date"].value(), thesis.deadline)

    def test_can_hand_in_thesis(self):
        """Hand In Date should default to deadline of thesis"""
        thesis = ThesisStub.applied(self.supervisor)
        thesis.restriction_note = True
        thesis.save()

        hand_in_date = thesis.deadline + timedelta(15)

        post_data = {
            'new_title': "A brand new title",
            'handed_in_date_day': str(hand_in_date.day),
            'handed_in_date_month': str(hand_in_date.month),
            'handed_in_date_year': str(hand_in_date.year),
            'restriction_note': 'on'
        }

        response = self.client.post(
            reverse('handin', args=[thesis.surrogate_key]), post_data)

        handed_in_thesis = Thesis.objects.get(
            surrogate_key=thesis.surrogate_key)

        self.assertEqual(302, response.status_code)
        self.assertEqual(Thesis.HANDED_IN, handed_in_thesis.status)
        self.assertEqual(hand_in_date, handed_in_thesis.handed_in_date)
        self.assertEqual(post_data["new_title"], handed_in_thesis.title)

    def test_validate_invalid_date(self):
        """Hand In Date should default to deadline of thesis"""
        thesis = ThesisStub.applied(self.supervisor)
        thesis.save()

        post_data = {
            'new_title': "A brand new title",
            'handed_in_date_day': "",
            'handed_in_date_month': "",
            'handed_in_date_year': "",
            'restriction_note': 'on'
        }

        response = self.client.post(
            reverse('handin', args=[thesis.surrogate_key]), post_data)

        self.assertEqual(200, response.status_code)
        self.assertIn('handed_in_date', response.context["form"].errors)

    def test_validate_new_title_missing(self):
        """Hand In Date should default to deadline of thesis"""
        thesis = ThesisStub.applied(self.supervisor)
        thesis.save()

        hand_in_date = thesis.deadline + timedelta(15)

        post_data = {
            'handed_in_date_day': str(hand_in_date.day),
            'handed_in_date_month': str(hand_in_date.month),
            'handed_in_date_year': str(hand_in_date.year),
            'restriction_note': 'on'
        }

        response = self.client.post(
            reverse('handin', args=[thesis.surrogate_key]), post_data)

        self.assertEqual(200, response.status_code)
        self.assertIn('new_title', response.context["form"].errors)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
from django.test.utils import setup_test_environment

from datetime import date

from website.models import *
from website.forms import HandInForm

setup_test_environment()


class FormHandInTests(TestCase):

    def test_initial_handed_in_date_is_due_date(self):
        """Should set handed_in_date to due_date
        for a thesis that has not been prolonged."""
        thesis = Thesis(
            begin_date=date(2018, 1, 1),
            due_date=date(2018, 3, 30),
            status=Thesis.APPLIED)

        form = HandInForm.initialize_from(thesis)

        self.assertEqual(thesis.due_date, form["handed_in_date"].value())

    def test_initial_handed_in_date_is_prolongation_date(self):
        """Should set handed_in_date to prlongation_date
        for a thesis that has been prolonged."""
        thesis = Thesis(
            begin_date=date(2018, 1, 1),
            due_date=date(2018, 3, 30),
            prolongation_date=date(2018, 6, 30),
            status=Thesis.PROLONGED)

        form = HandInForm.initialize_from(thesis)

        self.assertEqual(thesis.prolongation_date, form[
                         "handed_in_date"].value())

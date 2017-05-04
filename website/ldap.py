#!/usr/bin/env python3
import ldap

from thesispool.settings import *
from website.models import Supervisor


def get_supervisor(uid):
    con = ldap.initialize(AUTH_LDAP_SERVER_URI, trace_level=0)

    con.start_tls_s()

    dn = AUTH_LDAP_USER_DN_TEMPLATE % {'user': uid}

    results = con.search_s(dn, ldap.SCOPE_SUBTREE, "(objectClass=*)")

    return Supervisor(first_name=results[0][1]["givenName"][0].decode(),
                      last_name=results[0][1]["sn"][0].decode(),
                      initials=results[0][1]["initials"][0].decode(),
                      id=results[0][1]["uid"][0].decode())


def get_all_supervisors():
    con = ldap.initialize(AUTH_LDAP_SERVER_URI, trace_level=0)

    con.start_tls_s()

    _, entry = con.search_s(AUTH_LDAP_PROF_DN, ldap.SCOPE_BASE)[0]

    uids = [uid.decode() for uid in entry['memberUid']]

    return [get_supervisor(uid) for uid in uids]

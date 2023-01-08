import random
import string

from django.db import router


def get_using(instance):
    return router.db_for_write(instance.__class__, instance=instance)


def get_random_pic_name(length=20):
    return 'pic{}.jpg'.format(
        ''.join(random.choice(string.ascii_letters) for m in range(length)))

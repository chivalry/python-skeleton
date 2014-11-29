'''
This module contains a number of helper functions that instantiate
objects implmenting ``IPricer``

This module is intended to be used like so::

   from checkout import price, Product
   p = Product("apple", price.static(100))
   p = Product("orange", price.buy_n_get_m_free(3, 2))

'''

from datetime import datetime
from zope.interface import directlyProvides, implementer
from interface import IPricer


def static(price):
    '''
    Returns an object that implements IPricer with a static price.
    '''

    @implementer(IPricer)
    class StaticPricer(object):
        description = '$%0.2f each' % (price / 100.0)

        def __call__(self, count, **kw):
            return (price, price * count)
    return StaticPricer()


def cheap_after_dinner(price_before, price_after, dinnertime):
    '''
    Returns an object mplementing IPricer which gives a different
    price after dinnertime.
    '''
    @implementer(IPricer)
    class AfterDinnerPricer(object):
        description = "$%.2f before %02d00 hours, $%.2f after" %\
            (price_before / 100.0, dinnertime, price_after / 100.0)

        def __call__(self, count, **kw):
            if datetime.today().hour >= dinnertime:
                return (price_before, price_after * count)
            return (price_before, price_before * count)

    return AfterDinnerPricer()


def daily_special(price, day_of_week, discount):
    '''
    Returns an object that implements IPricer which is discounted a
    certain amount on particular day-of-the-week.
    '''
    def daily_special_pricer(count, **kw):
        myprice = price
        if datetime.today().weekday() == day_of_week:
            myprice = int(price * discount)
        return (myprice, myprice * count)
    weekdays = ['mon', 'tue', 'wed', 'thrs', 'fri', 'sat', 'sun']
    daily_special_pricer.description = '$%.2f each, %d%% off %s' % \
        (price / 100.0, (discount * 100), weekdays[day_of_week])

    directlyProvides(daily_special_pricer, IPricer)
    return daily_special_pricer


def buy_n_get_m_free(price, n, m):
    '''
    Returns an object that implements IPricer which does (a version
    of) "buy N get M free". For the border-case of wishing to purchase
    fewer than you're entitled to, we opt for "screw the customer",
    basically. Alternatively, we could provide a way to update the
    count to reflect the free items.

    For example, with "buy 5 get 2 free" if you buy 5 things, you
    still pay the same as if you bought 6 or 7.
    '''
    if m >= n:
        raise RuntimeError("Can't buy %d and get %d free." % (n, m))

    def buy_n_pricer(count, **kw):
        groups = count / (n + m)
        leftover = count % (n + m)
        free = groups * m
        paid = (groups * n)
        if leftover > n:
            paid = n
            free = leftover - n
        else:
            paid += leftover
        assert paid + free == count
        total = paid * price
        return (None, total)
    buy_n_pricer.description = 'Buy %d get %d free' % (n, m)
    directlyProvides(buy_n_pricer, IPricer)

    return buy_n_pricer

from braspag.core import BraspagRequest

payment_methods = []

for company, methods in BraspagRequest._PAYMENT_METHODS.items():
    for card, code in methods.items():
        payment_methods.append((code, '{0} {1}'.format(company, card)))

payment_methods.sort()

print '+' + 5 * '-' + '+' + 50 * '-' + '+'
print '|{0:^5}|{1:<50}|'.format('Code', 'Payment Method')
print '+' + 5 * '=' + '+' + 50 * '=' + '+'
for code, method in payment_methods:
    print '|{0:^5}|{1:<50}|'.format(code, method)
print '+' + 5 * '-' + '+' + 50 * '-' + '+'

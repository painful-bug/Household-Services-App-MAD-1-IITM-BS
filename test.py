import phonenumbers
from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type

number = "7047367553"
res = carrier._is_mobile(number_type(phonenumbers.parse(number)))
print(res)
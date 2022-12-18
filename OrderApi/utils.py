from PriceApi.models import Price


def get_price(distance, is_protected):        
    price =  Price.objects.first()
    km = float(distance)
    initial_price = price.initial_price
    anchor = price.anchor
    extra_price = 0
    money = 0
    max_km  = int(round(km))
    for i in range(1, max_km + 1):
        if i <= anchor:
            money += initial_price
        if i > anchor and (i - anchor) * price.price_percent <= 70:
            money += price.extra_price * (100 - (i - anchor) * price.price_percent) / 100; 
        if i > anchor and (i - anchor) * price.price_percent > 70:
            money += price.extra_price * 30 / 100;   
    if is_protected == 1:
        extra_price =  money * (price.price_protect / 100)
    return money + extra_price


# ---------------------------------------------------------------- durumlar
# Kural: dostane, sevimli klişeler (yemek, hava, spor, alışkanlık). Siyaset, savaş, sınır, din YOK.
# her ülke: (replik, ruh hali)  ruh hali: happy shock cool calm cry angry love sleepy shiver
SITUATIONS = {
    'snow': dict(title='COUNTRIES WHEN IT SNOWS', scene='snow', name='Snow', lines={
        'CA': ('Finally! Shorts weather.', 'cool'), 'BR': ('WHAT IS THIS?!', 'shiver'),
        'US': ('School is cancelled!', 'happy'), 'TR': ('Tea time, then.', 'calm'),
        'JP': ('So beautiful...', 'love'), 'MX': ('I am freezing!', 'shiver'),
        'DE': ('Trains still on time.', 'cool'), 'IN': ('My first snow!', 'shock'),
        'IT': ('Pasta will warm me.', 'happy'), 'GB': ('Bit chilly, innit.', 'calm'),
        'ES': ('Back to bed.', 'sleepy'), 'NL': ('Still biking.', 'cool')}),
    'heat': dict(title='COUNTRIES WHEN IT IS 35°C', scene='sun', name='Heatwave', lines={
        'CA': ('I am melting!', 'cry'), 'BR': ('Perfect beach day!', 'cool'),
        'GB': ('Hottest day ever!', 'shock'), 'IN': ('This is winter.', 'cool'),
        'ES': ('Siesta time.', 'sleepy'), 'DE': ('Where is the AC?!', 'angry'),
        'TR': ('Ice cream, please!', 'happy'), 'JP': ('Cold noodles time.', 'happy'),
        'MX': ('Add more chili.', 'cool'), 'US': ('AC on max!', 'happy'),
        'IT': ('Gelato for everyone!', 'love'), 'NL': ('Beach! Oh, rain.', 'cry')}),
    'breakfast': dict(title='COUNTRIES AT BREAKFAST', scene='kitchen', name='Breakfast', lines={
        'GB': ('Full English, please.', 'happy'), 'FR': ('Croissant and coffee.', 'love'),
        'US': ('Pancakes! Ten of them!', 'happy'), 'TR': ('Breakfast takes 3 hours.', 'love'),
        'JP': ('Rice, fish and miso.', 'calm'), 'DE': ('Bread. Lots of bread.', 'cool'),
        'IT': ('Just an espresso.', 'cool'), 'MX': ('Chilaquiles!', 'happy'),
        'IN': ('Chai and paratha!', 'happy'), 'NL': ('Sprinkles on bread!', 'love'),
        'BR': ('Cheese bread!', 'happy'), 'ES': ('Churros!', 'love')}),
    'football': dict(title='COUNTRIES DURING A FOOTBALL FINAL', scene='stadium', name='Football Final', lines={
        'BR': ('Samba time!', 'happy'), 'AR': ('Vamos! Vamos!', 'happy'),
        'DE': ('Efficiency wins.', 'cool'), 'GB': ("It's coming home!", 'love'),
        'US': ("It's called soccer.", 'calm'), 'IT': ('Defense is an art.', 'cool'),
        'ES': ('Tiki-taka!', 'happy'), 'FR': ('Allez les Bleus!', 'happy'),
        'JP': ('We clean the stadium after.', 'calm'), 'KR': ('Fighting!', 'angry'),
        'TR': ('Everyone outside! GOAL!', 'shock'), 'NL': ('Orange everywhere!', 'love'),
        'MX': ('Mexico! Mexico!', 'happy')}),
    'guests': dict(title='COUNTRIES WHEN GUESTS COME OVER', scene='living', name='Guests', lines={
        'TR': ('Eat! Eat more! Tea?', 'love'), 'IT': ('Mamma made pasta for 20.', 'happy'),
        'JP': ('Please take off your shoes.', 'calm'), 'DE': ('You are 2 minutes late.', 'angry'),
        'GB': ('Fancy a cuppa?', 'calm'), 'US': ('Make yourself at home!', 'happy'),
        'MX': ('Mi casa es su casa!', 'love'), 'IN': ('You will not leave hungry.', 'love'),
        'ES': ('Dinner at 10 PM.', 'cool'), 'FR': ('Wine? Cheese? Both.', 'cool'),
        'BR': ('Barbecue party!', 'happy'), 'KR': ('Shoes off, kimchi on!', 'happy')}),
    'newyear': dict(title="COUNTRIES ON NEW YEAR'S EVE", scene='night', name="New Year's Eve", lines={
        'JP': ('Bells and soba.', 'calm'), 'ES': ('Twelve grapes!', 'happy'),
        'BR': ('White clothes, beach!', 'happy'), 'US': ('Ball drop!', 'shock'),
        'GB': ('Big Ben countdown!', 'happy'), 'DE': ('Fireworks! MORE fireworks!', 'shock'),
        'TR': ('Pomegranate and family.', 'love'), 'IT': ('Red socks for luck!', 'happy'),
        'MX': ('Twelve wishes!', 'love'), 'KR': ('Everyone is one year older!', 'shock'),
        'NL': ('Oliebollen!', 'happy'), 'FR': ('Champagne!', 'cool')}),
    'rain': dict(title='COUNTRIES ON A RAINY DAY', scene='rain', name='Rainy Day', lines={
        'GB': ('Just normal weather.', 'calm'), 'IN': ('Monsoon party!', 'happy'),
        'NL': ('Still cycling.', 'cool'), 'BR': ('Rain? Still beach.', 'cool'),
        'JP': ('Umbrella ready.', 'calm'), 'ES': ('Rain? Stay home.', 'sleepy'),
        'DE': ('Raincoat, of course.', 'cool'), 'US': ('Rain delay!', 'cry'),
        'CA': ('Rain or snow, same.', 'calm'), 'TR': ('Tea time again.', 'love')}),
    'monday': dict(title='COUNTRIES ON MONDAY MORNING', scene='city', name='Monday Morning', lines={
        'DE': ('At work since 7.', 'cool'), 'ES': ('Five more minutes...', 'sleepy'),
        'US': ('Coffee. BIG coffee.', 'sleepy'), 'BR': ('Still Carnival in my heart.', 'happy'),
        'GB': ('Tea first.', 'calm'), 'FR': ('Café first.', 'calm'),
        'IT': ('Espresso, then talk.', 'angry'), 'TR': ('Tea, then traffic.', 'calm'),
        'KR': ('Hurry! Hurry!', 'shock'), 'MX': ('Café de olla, vamos.', 'happy'),
        'IN': ('Traffic jam again.', 'cry'), 'JP': ('Work, work, work!', 'shock')}),
    'internet': dict(title='COUNTRIES WHEN THE INTERNET GOES DOWN', scene='living', name='No Internet', lines={
        'KR': ('Impossible! We have the fastest!', 'shock'), 'US': ('I cannot live like this!', 'cry'),
        'JP': ('I will read a book.', 'calm'), 'DE': ('Never worked anyway.', 'cool'),
        'TR': ('Finally, a real chat.', 'happy'), 'GB': ("Let's have tea.", 'calm'),
        'IN': ('Restart the router!', 'angry'), 'BR': ('Football outside!', 'happy'),
        'IT': ('Time for a long lunch.', 'love'), 'NL': ('Biking it is.', 'cool'),
        'ES': ('Siesta time.', 'sleepy'), 'FR': ('Philosophy time.', 'cool')}),
    'birthday': dict(title='COUNTRIES AT A BIRTHDAY PARTY', scene='party', name='Birthday Party', lines={
        'MX': ('Piñata time!', 'happy'), 'TR': ('Cake and tea!', 'love'),
        'KR': ('Seaweed soup!', 'happy'), 'IT': ('Tiramisu!', 'love'),
        'US': ('Giant cake!', 'shock'), 'GB': ('Hip hip hooray!', 'happy'),
        'DE': ('Never celebrate early!', 'angry'), 'JP': ('Cake and karaoke!', 'happy'),
        'BR': ('Brigadeiros!', 'love'), 'IN': ('Sweets for everyone!', 'happy'),
        'NL': ('Congrats to everyone!', 'happy'), 'ES': ('Pull the ears!', 'happy')}),
    'sneeze': dict(title='COUNTRIES WHEN SOMEONE SNEEZES', scene='city', name='Sneeze', lines={
        'DE': ('Gesundheit!', 'cool'), 'US': ('Bless you!', 'happy'), 'ES': ('¡Salud!', 'happy'),
        'TR': ('Çok yaşa!', 'love'), 'IT': ('Salute!', 'happy'), 'FR': ('À tes souhaits!', 'calm'),
        'JP': ('...(polite silence)', 'calm'), 'GB': ('Bless you. Sorry.', 'calm'),
        'BR': ('Saúde!', 'happy'), 'MX': ('¡Salud!', 'happy'), 'NL': ('Gezondheid!', 'cool')}),
    'dinner': dict(title='COUNTRIES AT DINNER TIME', scene='kitchen', name='Dinner Time', lines={
        'ES': ('Dinner at 11 PM!', 'cool'), 'DE': ('Dinner at 6 sharp.', 'cool'),
        'IT': ('Pasta, of course.', 'love'), 'JP': ('Itadakimasu!', 'happy'),
        'TR': ('Everyone at the table!', 'love'), 'US': ('Burgers!', 'happy'),
        'IN': ('Curry with family!', 'love'), 'MX': ('Tacos!', 'happy'), 'FR': ('Three courses!', 'cool'),
        'KR': ('Korean barbecue!', 'happy'), 'BR': ('Rice and beans!', 'happy'), 'GB': ('Fish and chips!', 'happy')}),
}

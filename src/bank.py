

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

# 2026-10-12: tekrar riskine karşı 14 durum daha (toplam 26)
SITUATIONS.update({
    'traffic': dict(title='COUNTRIES IN A TRAFFIC JAM', scene='city', name='Traffic Jam', lines={
        'IN': ('Honk honk honk!', 'happy'), 'DE': ('Stay in your lane.', 'angry'), 'IT': ('I will make my own lane!', 'angry'),
        'JP': ('Silent and patient.', 'calm'), 'US': ('Bigger truck, no problem.', 'cool'), 'TR': ('Simit seller! Over here!', 'happy'),
        'GB': ('Sorry, after you.', 'calm'), 'BR': ('Music up, windows down!', 'happy'), 'MX': ('Tacos from the car.', 'love'),
        'NL': ('I took the bike.', 'cool'), 'KR': ('Hurry, hurry!', 'shock'), 'FR': ('Croissant break.', 'calm')}),
    'exam': dict(title='COUNTRIES THE NIGHT BEFORE AN EXAM', scene='living', name='Exam Night', lines={
        'KR': ('Studying since 5 AM.', 'shock'), 'IN': ('Chai and books all night!', 'cool'), 'US': ('Who needs sleep?', 'cry'),
        'JP': ('Notes are color coded.', 'calm'), 'BR': ('Tomorrow is a new day.', 'sleepy'), 'DE': ('Plan made weeks ago.', 'cool'),
        'TR': ('Mom made tea. Again.', 'love'), 'IT': ('Pasta for brain power.', 'happy'), 'ES': ('Siesta first.', 'sleepy'),
        'GB': ('Keep calm and revise.', 'calm'), 'FR': ('Philosophy exam? Easy.', 'cool'), 'MX': ('Coffee number five.', 'shock')}),
    'vacation': dict(title='COUNTRIES ON SUMMER VACATION', scene='sun', name='Summer Vacation', lines={
        'DE': ('Towel on the chair at 6 AM.', 'cool'), 'GB': ('Sunburn in ten minutes.', 'cry'), 'US': ('Disney again!', 'happy'),
        'TR': ('Whole family, one car!', 'love'), 'JP': ('Two hundred photos.', 'happy'), 'IT': ('August? Everyone at the beach.', 'cool'),
        'BR': ('Beach every day!', 'happy'), 'IN': ('Family trip! All 30 of us.', 'happy'), 'FR': ('Whole August off.', 'cool'),
        'ES': ('Tourists everywhere!', 'shock'), 'NL': ('Camping with the caravan.', 'happy'), 'CA': ('Lake and canoe.', 'calm')}),
    'coffee': dict(title='COUNTRIES ORDERING COFFEE', scene='kitchen', name='Coffee Order', lines={
        'IT': ('Espresso. Standing up.', 'cool'), 'US': ('Venti iced caramel, extra shot!', 'happy'), 'TR': ('Turkish coffee, read my cup!', 'love'),
        'FR': ('Café crème, s\'il vous plaît.', 'calm'), 'GB': ('Actually, tea please.', 'calm'), 'BR': ('Cafezinho!', 'happy'),
        'JP': ('Canned coffee from a machine.', 'happy'), 'KR': ('Iced Americano. Even in winter.', 'cool'),
        'IN': ('Filter coffee!', 'happy'), 'MX': ('Café de olla!', 'love'), 'ES': ('Café con leche.', 'calm'),
        'DE': ('Filter coffee. Black.', 'cool')}),
    'wedding': dict(title='COUNTRIES AT A WEDDING', scene='party', name='Wedding', lines={
        'IN': ('Three days of dancing!', 'happy'), 'TR': ('Pin money on the bride!', 'love'), 'IT': ('Ten-course dinner!', 'love'),
        'US': ('Open bar!', 'happy'), 'GB': ('Speeches, then tea.', 'calm'), 'MX': ('Mariachi band!', 'happy'),
        'JP': ('Envelope with new bills.', 'calm'), 'DE': ('Start at 2 PM sharp.', 'cool'), 'BR': ('Party until sunrise!', 'happy'),
        'KR': ('Photos with everyone.', 'happy'), 'ES': ('Dinner at midnight!', 'cool'), 'FR': ('Wine, cheese, wine.', 'love')}),
    'battery': dict(title='COUNTRIES WHEN THE PHONE IS AT 1%', scene='living', name='Phone at 1%', lines={
        'US': ('Nooo! My streak!', 'cry'), 'KR': ('Power bank, always.', 'cool'), 'JP': ('Charger in my bag.', 'calm'),
        'IN': ('Borrow a charger from a neighbor!', 'happy'), 'TR': ('Who has a charger?!', 'shock'), 'DE': ('Phone off. Problem solved.', 'cool'),
        'BR': ('Dancing to save battery.', 'happy'), 'GB': ('Brilliant. Just brilliant.', 'calm'), 'IT': ('Call mamma, quick!', 'shock'),
        'MX': ('One more video...', 'sleepy'), 'FR': ('Back to paper maps.', 'calm'), 'ES': ('Siesta for the phone too.', 'sleepy')}),
    'lost': dict(title='COUNTRIES WHEN THEY GET LOST', scene='city', name='Lost', lines={
        'US': ('GPS says turn left. Into a lake.', 'shock'), 'JP': ('Ask a stranger politely.', 'calm'), 'DE': ('I have a paper map.', 'cool'),
        'TR': ('Ask the shop owner, he knows!', 'happy'), 'IT': ('Follow the smell of pasta.', 'love'), 'GB': ('Sorry, which way is north?', 'calm'),
        'BR': ('Lost? Make new friends!', 'happy'), 'IN': ('Everyone gives different directions!', 'shock'), 'FR': ('Not lost. Exploring.', 'cool'),
        'MX': ('Follow the music!', 'happy'), 'KR': ('Subway app, always.', 'cool'), 'NL': ('Follow the bike lane.', 'calm')}),
    'spicy': dict(title='COUNTRIES EATING SPICY FOOD', scene='kitchen', name='Spicy Food', lines={
        'MX': ('Not spicy at all.', 'cool'), 'IN': ('Mild. Very mild.', 'cool'), 'KR': ('Fire noodles! Easy!', 'happy'),
        'GB': ('Pepper is spicy enough.', 'cry'), 'DE': ('Water! WATER!', 'shock'), 'US': ('Hot wings challenge!', 'shock'),
        'TR': ('More chili flakes please.', 'happy'), 'JP': ('Wasabi... too much!', 'cry'), 'IT': ('A little chili oil.', 'calm'),
        'BR': ('Hot sauce on everything!', 'happy'), 'NL': ('Mayo, please.', 'calm'), 'FR': ('Too spicy for my wine.', 'angry')}),
    'momcalls': dict(title='COUNTRIES WHEN MOM CALLS', scene='living', name='Mom Calls', lines={
        'IT': ('Yes mamma, I ate!', 'love'), 'TR': ('Did you wear a jacket?', 'love'), 'IN': ('Video call with all relatives!', 'happy'),
        'MX': ('Sí, mamá. Sí, mamá.', 'calm'), 'US': ('Call you back, mom!', 'cool'), 'KR': ('Did you eat rice?', 'love'),
        'BR': ('Mom! I miss you!', 'love'), 'GB': ('All fine, mum. Weather is bad.', 'calm'), 'DE': ('Scheduled call, 6 PM.', 'cool'),
        'JP': ('I am working hard, mom.', 'calm'), 'ES': ('Two hours later...', 'sleepy'), 'FR': ('Oui, maman.', 'calm')}),
    'gym': dict(title='COUNTRIES AT THE GYM', scene='city', name='Gym', lines={
        'US': ('Protein shake time!', 'happy'), 'BR': ('Leg day, every day!', 'cool'), 'DE': ('Sets, reps, schedule.', 'cool'),
        'IT': ('Gym? Look good first.', 'love'), 'KR': ('Cardio at 6 AM.', 'shock'), 'JP': ('Clean the machine after.', 'calm'),
        'TR': ('Then kebab, of course.', 'happy'), 'GB': ('Gym, then pub.', 'happy'), 'IN': ('Yoga is better.', 'calm'),
        'MX': ('Tacos give energy!', 'happy'), 'NL': ('I biked here. Done.', 'cool'), 'FR': ('Sport? Non.', 'sleepy')}),
    'queue': dict(title='COUNTRIES WAITING IN LINE', scene='city', name='Waiting in Line', lines={
        'GB': ('Perfect queue. Lovely.', 'love'), 'JP': ('Line for the new bakery.', 'calm'), 'DE': ('Take a number.', 'cool'),
        'IT': ('What line?', 'happy'), 'IN': ('Line? Everyone at once!', 'shock'), 'US': ('Is there a drive-thru?', 'cool'),
        'TR': ('My cousin works here!', 'happy'), 'BR': ('Making friends in the line.', 'happy'), 'KR': ('Online booking. No line.', 'cool'),
        'FR': ('Complaining while waiting.', 'angry'), 'ES': ('Line for churros!', 'love'), 'MX': ('Line for tacos!', 'love')}),
    'payday': dict(title='COUNTRIES ON PAYDAY', scene='city', name='Payday', lines={
        'US': ('Online shopping cart, full!', 'happy'), 'DE': ('Straight to savings.', 'cool'), 'IT': ('New shoes!', 'love'),
        'TR': ('Bills, bills, bills.', 'cry'), 'JP': ('Save for next month.', 'calm'), 'BR': ('Barbecue for everyone!', 'happy'),
        'IN': ('Gold for mom!', 'love'), 'GB': ('Pub round on me!', 'happy'), 'KR': ('Chicken and beer night!', 'happy'),
        'MX': ('Taco party!', 'happy'), 'ES': ('Tapas night!', 'happy'), 'FR': ('Fancy dinner.', 'cool')}),
    'tea': dict(title='COUNTRIES WHEN SOMEONE OFFERS TEA', scene='kitchen', name='Tea Time', lines={
        'GB': ('Milk first? NEVER.', 'angry'), 'TR': ('Tenth glass, please!', 'love'), 'IN': ('Masala chai!', 'happy'),
        'JP': ('Matcha ceremony.', 'calm'), 'US': ('Iced and sweet, please.', 'happy'), 'KR': ('Barley tea!', 'happy'),
        'DE': ('Herbal tea. For health.', 'cool'), 'IT': ('Tea? I want espresso.', 'shock'), 'MX': ('Hot chocolate instead.', 'love'),
        'BR': ('Mate? Let us share!', 'happy'), 'FR': ('Tea... how British.', 'cool'), 'NL': ('Tea and a cookie.', 'calm')}),
    'halloween': dict(title='COUNTRIES ON HALLOWEEN', scene='night', name='Halloween', lines={
        'US': ('Candy! All the candy!', 'happy'), 'MX': ('Day of the Dead is coming!', 'love'), 'GB': ('Pumpkin carving!', 'happy'),
        'JP': ('Best costume parade!', 'happy'), 'DE': ('Too loud.', 'angry'), 'TR': ('What is this holiday?', 'shock'),
        'IE': ('We invented it!', 'cool'), 'CA': ('Trick or treat in the snow.', 'shiver'), 'KR': ('Costume party!', 'happy'),
        'IT': ('Pasta in a pumpkin!', 'love'), 'BR': ('Party, of course!', 'happy'), 'IN': ('Sweets? I have Diwali!', 'happy')}),
})

import json

with open('data/business.json', 'r', encoding='utf-8') as fin,open('data/UCbusiness.json', 'w', encoding='utf-8') as fout:
	for i in fin:
		j = i.strip()
		if 'Restaurants' not in j:continue
		text = json.loads(j)
		if text["is_open"] != 1: continue
		if 'state' not in text:continue
		if 'city' not in text:continue
		if 'hours' not in text:continue
		if text['state']!='IL':continue
		if text['city']!='Champaign' and text['city']!='Urbana':continue

		if "attributes" not in text:continue
		attributes = text["attributes"]
		if attributes == None:continue
		#
		fout.write(i)

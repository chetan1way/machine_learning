from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_sdk import Action
from rasa_sdk.events import SlotSet
from rasa_sdk.events import FollowupAction
import pandas as pd
import json
import smtplib
from email.message import EmailMessage

ZomatoData = pd.read_csv('zomato.csv')
ZomatoData = ZomatoData.drop_duplicates().reset_index(drop=True)
WeOperate = ['New Delhi', 'Gurgaon', 'Noida', 'Faridabad', 'Allahabad', 'Bhubaneshwar', 'Mangalore', 'Mumbai', 'Ranchi', 'Patna', 'Mysore', 'Aurangabad', 'Amritsar', 'Puducherry', 'Varanasi', 'Nagpur', 'Vadodara', 'Dehradun', 'Vizag', 'Agra', 'Ludhiana', 'Kanpur', 'Lucknow', 'Surat', 'Kochi', 'Indore', 'Ahmedabad', 'Coimbatore', 'Chennai', 'Guwahati', 'Jaipur', 'Hyderabad', 'Bangalore', 'Nashik', 'Pune', 'Kolkata', 'Bhopal', 'Goa', 'Chandigarh', 'Ghaziabad', 'Ooty', 'Gangtok', 'Shimla']

fin_res = ''

def RestaurantSearch(City,Cuisine,Price):
    lower_price_range = 0
    upper_price_range = 300

    if Price == 'Low':
    	lower_price_range = 0
    	upper_price_range = 300
    if Price == 'Mid':
        lower_price_range = 300
        upper_price_range = 700
    if Price == 'High':
        lower_price_range = 700
        upper_price_range = 100000
    
    print('in restaurnat seach')
    print(lower_price_range,upper_price_range)
    print('City',City)
    print('Cuisine',Cuisine)
    print('Price',Price)
        
    TEMP = ZomatoData[(ZomatoData['Cuisines'].apply(lambda x: Cuisine.lower() in x.lower())) & 
                      (ZomatoData['City'].apply(lambda x: City.lower() in x.lower())) &
                      ((ZomatoData['Average Cost for two'] > lower_price_range) & (ZomatoData['Average Cost for two'] <= upper_price_range))]
    TEMP= TEMP.sort_values(by=['Aggregate rating'], ascending=False)
    return TEMP[['Restaurant Name','Address','Average Cost for two','Aggregate rating']]



class ActionSearchRestaurants(Action):
	def name(self):
		return 'action_search_restaurants'

	def run(self, dispatcher, tracker, domain):
		#config={ "user_key":"f4924dc9ad672ee8c4f8c84743301af5"}
		print('in ActionSearchRestaurants')
		loc = tracker.get_slot('location')
		cuisine = tracker.get_slot('cuisine')
		price = tracker.get_slot('price')
		results = RestaurantSearch(City=loc,Cuisine=cuisine,Price=price)
		response=""
		if results.shape[0] == 0:
			response= "no results"
		else:
			for restaurant in results.iloc[:5].iterrows():
				restaurant = restaurant[1]
				response=response + F"Found {restaurant['Restaurant Name']} in {restaurant['Address']} rated {restaurant['Address']} with avg cost {restaurant['Average Cost for two']} \n\n"
			global fin_res
			fin_res = response
			dispatcher.utter_message("-----"+fin_res)
			return [SlotSet('location',loc)]

class ActionSendMail(Action):
	def name(self):
		return 'action_send_mail'

	def run(self, dispatcher, tracker, domain):
		MailID = tracker.get_slot('mail_id')
		#sendmail(MailID,response)
		print('in ActionSendMail')
		print('Your Mail',MailID)
		server = smtplib.SMTP('smtp.gmail.com', 587)
		server.starttls()
		server.login('chetan.wanave07@gmail.com', 'uvbxpcoskscqazda')

		msg = EmailMessage()
		thank_msg = 'Thank You For contacting Foodie. '
		global fin_res
		print(fin_res)

		message = thank_msg+'\n'+fin_res+'\n'
		msg.set_content(message)
		msg['Subject'] = 'Foodie restaurant search result'
		msg['From'] = 'Foodie@gmail.com'
		msg['To'] = MailID
		server.send_message(msg)

		return [SlotSet('mail_id',MailID)]

class ActionSearchLoc(Action):
	def name(self):
		return 'action_search_loc'

	def run(self, dispatcher, tracker, domain):
		loc = tracker.get_slot('location')
		loc = loc.lower()
		response=""
		print('Selected location:-',loc)
		print('in loc search')
		if loc not in [x.lower() for x in WeOperate]:
			print('Selected location:-',loc)
			response= "We Dont operate in this city,Can you please specify some other location"
			dispatcher.utter_message("-----"+response)
			return [FollowupAction("utter_ask_location")]
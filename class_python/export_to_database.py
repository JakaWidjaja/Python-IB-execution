#import login_to_db
import time

class export_to_database(login_to_db.login_to_db):

    def export_futures(self, bid_price, ask_price, month_expiry, year_expiry, database_table):

        self.bid_price = bid_price
        self.ask_price = ask_price
        self.database_table = database_table
        self.month_expiry = month_expiry
        self.year_expiry = year_expiry

        #Stuff to access MySQL databases. 
        quant_trading_database = super().login_to_quant_trading()
        cursor = quant_trading_database.cursor()

        #Table name.
        table_name = self.database_table

        #Creating insert command into database. 
        sql_insert_querry = " INSERT INTO " +  table_name + \
                            "(date_time, bid, ask, month_expiry, year_expiry) VALUES (%s, %s, %s, %s, %s)"
        insert_data = (time.time(), self.bid_price, self.ask_price, self.month_expiry, self.year_expiry)

        #Execute querry
        cursor.execute(sql_insert_querry, insert_data)
        quant_trading_database.commit()

    def export_option(self, premium_bid, premium_ask,
                            strike, 
                            implied_vol_bid,
                            implied_vol_ask,
                            month_expiry,
                            year_expiry,
                            database_table):
        
        self.premium_bid = premium_bid
        self.premium_ask = premium_ask
        self.strike = strike
        self.implied_vol_bid = implied_vol_bid
        self.implied_vol_ask = implied_vol_ask
        self.month_expiry = month_expiry
        self.year_expiry = year_expiry
        self.database_table = database_table

        #Stuff to access MySQL databases. 
        quant_trading_database = super().login_to_quant_trading()
        cursor = quant_trading_database.cursor()

        #Table name.
        table_name = self.database_table

        #Creating insert command into database. 
        sql_insert_querry = " INSERT INTO " +  table_name + \
                            "(date_time, premium_bid, premium_ask, \
                                         strike,\
                                         implied_vol_bid, implied_vol_ask, \
                                         month_expiry, \
                                         year_expiry) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        insert_data = (time.time(), self.premium_bid, self.premium_ask, 
                                    self.strike,
                                    self.implied_vol_bid, self.implied_vol_ask,
                                    self.month_expiry,
                                    self.year_expiry)

        #Execute querry
        cursor.execute(sql_insert_querry, insert_data)
        quant_trading_database.commit()


    def export_fx(self, bid_price, ask_price, database_table):

        self.bid_price = bid_price
        self.ask_price = ask_price
        self.database_table = database_table

        #Stuff to access MySQL databases. 
        quant_trading_database = super().login_to_quant_trading()
        cursor = quant_trading_database.cursor()

        #Creating insert command into database. 
        sql_insert_querry = " INSERT INTO " +  self.database_table + \
                            "(date_time, bid, ask) VALUES (%s, %s, %s)"
        insert_data = (time.time(), self.bid_price, self.ask_price)

        #Execute querry
        cursor.execute(sql_insert_querry, insert_data)
        quant_trading_database.commit()

    def export_equity(self, asset_name, bid_price, ask_price, database_table):
        #Initialise arguments
        self.asset_name = asset_name
        self.bid_price = bid_price
        self.ask_price = ask_price
        self.database_table = database_table

        #Stuff to access MySQL databases. 
        quant_trading_database = super().login_to_quant_trading()
        cursor = quant_trading_database.cursor()

        #creating insert command into database. 
        sql_insert_querry = " INSERT INTO " + self.database_table + \
                            "(name, date_time, bid, ask) VALUES (%s, %s, %s, %s)"
        insert_data = (self.asset_name, time.time(), self.bid_price, self.ask_price)

        #Execute querry
        cursor.execute(sql_insert_querry, insert_data)
        quant_trading_database.commit()
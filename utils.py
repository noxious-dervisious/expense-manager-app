from ruamel.yaml import YAML
import logging
import csv
import datetime
from constants import *
import uuid
import hashlib

yaml = YAML()

class Utils:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data = {}
        self.start,self.end = self.load_start_end_date()
    
    def __type_casting(self,row,is_abs=False):
        # row["kind"] = "Credit"
        for k,v in row.items():
            if v.replace('-','').isdigit() and k != "Date":
                # if '-' in v:
                #     row["kind"] = "Debit"
                if is_abs:
                    row[k] = abs(int(v))
                else:
                    row[k] = int(v)
            if k == 'Date':
                row[k] = datetime.datetime.strptime(v,"%Y-%m-%d").date()
        return row
    
    def __check_data_exists(self):
        if self.data is None:
            self.data = {}

    def load_start_end_date(self):
        self.load_profile_config()
        month = datetime.datetime.now().month
        year = datetime.datetime.now().year
        start = datetime.datetime(year, month-1, self.profile.get("salary_date",1)).date()
        if month == 1:
            start = datetime.datetime(year-1, 12, self.profile.get("salary_date",1)).date()    
        if month == 12:
            end = datetime.datetime(year + 1, 1, self.profile.get("salary_date",1)).date()
        else:
            end = datetime.datetime(year, month, self.profile.get("salary_date",1)).date()
        return (start,end)

    def load_profile_config(self):
        try:
            self.data = yaml.load(open(PROFILE_FILE_NAME))
            self.__check_data_exists()
            self.profile = self.data.get("profile",{})
        except:
            self.logger.info("Unable to load `profile.yaml` file")
            # self.data = {}
            self.profile = {}

    def dump_profile_config(self):
        try:
            self.data["profile"] = self.profile
            yaml.dump(self.data,open(PROFILE_FILE_NAME,'w'))
        except Exception as er:
            self.logger.error(er)

    def load_investment_profile(self):
        try:
            self.data = yaml.load(open(PROFILE_FILE_NAME))
            self.__check_data_exists()
            self.investment = self.data.get("investment",{})
        except:
            self.logger.info("Unable to load `profile.yaml` file")
            # self.data = {}
            self.investment = {}

    def dump_investment_profile(self):
        try:
            self.data["investment"] = self.investment
            yaml.dump(self.data,open(PROFILE_FILE_NAME,'w'))
        except Exception as er:
            self.logger.error(er)

    def load_vendor_config(self):
        try:
            self.data = yaml.load(open(PROFILE_FILE_NAME))
            self.__check_data_exists()
            self.vendors = self.data.get("vendors",[])
        except:
            self.logger.info("Unable to load `profile.yaml` file")
            # self.data = {}
            self.vendors = []

    def dump_vendor_file(self):
        try:
            self.data["vendors"] = self.vendors
            yaml.dump(self.data,open(PROFILE_FILE_NAME,'w'))
        except Exception as er:
            self.logger.error(er)

    def load_categories_file(self):
        try:
            self.data = yaml.load(open(PROFILE_FILE_NAME))
            self.__check_data_exists()
            self.categories = self.data.get("categories",[])
        except Exception as er:
            self.logger.error(f"Failed to dump data in the file {PROFILE_FILE_NAME}, {er}")
            self.logger.error(er)
            # self.data = {}
            self.categories = []

    def dump_catogories_file(self):
        try:
            self.data["categories"] = self.categories
            yaml.dump(self.data,open(PROFILE_FILE_NAME,'w'))
        except Exception as er:
            self.logger.error(f"Failed to dump data in the file {PROFILE_FILE_NAME}, {er}")

    def load_payment_methods(self):
        try:
            self.data = yaml.load(open(PROFILE_FILE_NAME))
            self.__check_data_exists()
            self.payment_methods = self.data.get("payment_methods",[])
        except:
            self.logger.info("Unable to load `profile.yaml` file")
            # self.data = {}
            self.payment_methods = []

    def dump_payment_methods(self):
        try:
            self.data["payment_methods"] = self.payment_methods
            yaml.dump(self.data,open(PROFILE_FILE_NAME,'w'))
        except Exception as er:
            self.logger.error(er)
    
    def load_budget_info(self):
        try:
            self.data = yaml.load(open(PROFILE_FILE_NAME))
            self.__check_data_exists()
            self.budegting_tool = self.data.get("budgeting_tool",[])
            if self.budegting_tool is None:
                self.budegting_tool = []
        except:
            self.logger.info("Unable to load `profile.yaml` file")
            # self.data = {}
            self.budegting_tool = []

    def dump_budget_info(self):
        try:
            self.data["budgeting_tool"] = self.budegting_tool
            yaml.dump(self.data,open(PROFILE_FILE_NAME,'w'))
        except Exception as er:
            self.logger.error(er)

    def load_all_configs(self):
        self.load_categories_file()
        self.load_payment_methods()
        self.load_vendor_config()

    def load_transactions_file(self)->list[dict]:
        try:
            self.transactions = []
            reader = csv.DictReader(open(TRANSACTIONS_FILE_NAME))
            for rows in reader:
                self.transactions.append(self.__type_casting(rows))
        except Exception as er:
            self.logger.error(er)
            self.transactions = []
    
    def dump_transactions_file(self,dt=None):
        try:
            if dt is not None:
                with open(TRANSACTIONS_FILE_NAME,'a',newline='\n') as file:
                    writer = csv.DictWriter(file,fieldnames=[dt["name"] for dt in TRANSACTION_FIELD_NAMES])
                    file.seek(0,2)
                    if file.tell() == 0:
                        writer.writeheader()
                    writer.writerow(dt)
            else:
                with open(TRANSACTIONS_FILE_NAME,'w',newline='\n') as file:
                    writer = csv.DictWriter(file,fieldnames=[dt["name"] for dt in TRANSACTION_FIELD_NAMES])
                    writer.writeheader()
                    for transaction in self.transactions:
                        writer.writerow(transaction)

        except Exception as er:
            self.logger.error(f"DAMN!!! I am not able to write to your transactions file {er}")

    def dump_recurring_transactions_file(self,dt=None):
        try:
            if dt is not None:
                with open(RECURRING_FILE_NAME,'a',newline='\n') as file:
                    writer = csv.DictWriter(file,fieldnames=[dt["name"] for dt in TRANSACTION_FIELD_NAMES])
                    file.seek(0,2)
                    if file.tell() == 0:
                        writer.writeheader()
                    writer.writerow(dt)
            else:
                with open(RECURRING_FILE_NAME,'w',newline='\n') as file:
                    writer = csv.DictWriter(file,fieldnames=[dt["name"] for dt in TRANSACTION_FIELD_NAMES])
                    writer.writeheader()
                    for transaction in self.recurring:
                        writer.writerow(transaction)

        except Exception as er:
            self.logger.error(f"DAMN!!! I am not able to write to your transactions file {er}")

    def load_recurring_payments_file(self,is_abs=False)->list[dict]:
        try:
            self.recurring = []
            reader = csv.DictReader(open(RECURRING_FILE_NAME))
            for rows in reader:
                self.recurring.append(self.__type_casting(rows,is_abs))
        except Exception as er:
            self.logger.error(er)
            self.recurring = []

    def get_list_of_banks(self):
        return set([payment["bank"] for payment in self.payment_methods])
    
    def get_list_of_vendors(self):
        return set([vendor["name"] for vendor in self.vendors])
    
    def map_vendor_to_category(self,vendor_name):
        try:
            return [vendor["category"] for vendor in self.vendors if vendor["name"] == vendor_name][0]
        except:
            return "Misc"
    def map_bank_to_modes(self,bank):
        return [payment["mode"] for payment in self.payment_methods if payment["bank"] == bank]
    
    def get_parent_account(self,bank,mode):
        self.load_payment_methods()
        return [payment["associated_account_number"] for payment in self.payment_methods if payment["bank"] == bank and payment["mode"] == mode][0]
    
    def adjust_associated_bank_balance(self,uid,value):
        self.load_payment_methods()
        for idx,payment in enumerate(self.payment_methods):
            if payment["uid"] == uid:
                self.payment_methods[idx]["balance"] += value
                break
        self.dump_payment_methods()

    def generate_uuid(self):
        return str(uuid.uuid4())
    
    
    def get_cashback_percentage(self,dt):
        self.load_payment_methods()
        for payment in self.payment_methods:
            if dt["Payment Method"] == payment["bank"] and dt["Payment Mode"] == payment["mode"]:
                return payment["cashback"]/100

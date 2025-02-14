from ninja import NinjaAPI, Schema
from django.shortcuts import get_object_or_404
# importing database models
from .models import UserApiKey, Transaction, UserWallet

# utils file
from .utils import generate_api_key

# imported python module
from pydantic import UUID4
from datetime import date
from decimal import Decimal
from datetime import datetime

#initiate Ninja API
api = NinjaAPI()

SECRET_KEY = "jHnHG86273nKgD770l2aas125miihbVRGpPjGfRrrgjnmPmmQD0d83"
# Schemas statically define the data neede for requests




class TransactionCreditCreate(Schema):
    uuid: str
    description: str
    amount: Decimal

class RegenApiKey(Schema):
    uuid: str

class CreateUserID(Schema):
    secret_key: str

class AddFunds(Schema):
    amount: int
    uuid: str

class UserTransactionsGet(Schema):
    uuid: str

class CheckBalance(Schema):
    uuid: str


# all endpoints here


# test
@api.get("/test")
def hello(request):
    return {"message": "Test works!"}




#creates new userid with api key adn time created
@api.post("/newuserid")
def create_api_key(request, createuserid: CreateUserID):

    if createuserid.secret_key != SECRET_KEY:
        return {"error": "incorrect secret key"}

    # creates the user uuid, an initial API key and the time
    new_key = generate_api_key()

    time_now = datetime.now()

    api_model = UserApiKey.objects.create(key=new_key, created_at=time_now)
    # will row of data in ApiKey table for this UUID
    return api_model



@api.post("/regenerateapikey")
def update_api_key(request, regenapikey: RegenApiKey, api_key: str):
    # if api key doesn't exist it will return 404
    user_api_key = get_object_or_404(UserApiKey, key=api_key)
    try:
        # Retrieve the UserApiKey instance by uuid
        #user_api_key = UserApiKey.objects.get(uuid=payload.uuid) # this is another valid way to do this
        user_api_key_row = get_object_or_404(UserApiKey, uuid=regenapikey.uuid)

        try:

            # Update the key and created_at fields
            user_api_key_row.key = generate_api_key()  # Replace with your logic to generate a new API key
            user_api_key_row.created_at = datetime.now()

            # Save the changes
            user_api_key_row.save()

            # Return the updated object
            return user_api_key_row

        except:
            return {"error": "failed to generate and save api key"}, 404

    except UserApiKey.DoesNotExist:
        return {"error": "UserApiKey not found"}, 404



@api.get("/listalltransactions")
def list_transactions(request, secret_key: str):
    if secret_key != SECRET_KEY:
        return {"error": "incorrect secret key"}
    return list(Transaction.objects.all())


# Create a Credit Transaction
@api.post("/createtransaction")
def create_transaction(request, transactioncreditcreate: TransactionCreditCreate, api_key: str):
    # if api key doesn't exist it will return 404
    user_api_key = get_object_or_404(UserApiKey, key=api_key) # not using this variable

    uuid = transactioncreditcreate.uuid
    user_wallet = get_object_or_404(UserWallet, uuid=uuid)

    description = transactioncreditcreate.description
    amount = transactioncreditcreate.amount
    try:
        transaction = Transaction.objects.create(uuid=uuid, api_key=api_key, description=description, amount=amount)

        newbalance = user_wallet.balance + amount
        user_wallet.balance += amount
        user_wallet.save()

        return {"message": f"transactio successful", "new balance": f"{newbalance}"}



    except Exception as e:
        return {"error": str(e)}




@api.get("/getusertransactions")
def add_funds(request, usertransactionsget: UserTransactionsGet, api_key:str):
    # if api key doesn't exist it will return 404
    user_api_key = get_object_or_404(UserApiKey, key=api_key)
    # check if uuid exists
    uuid =  usertransactionsget.uuid
    user_wallet = get_object_or_404(UserWallet, uuid=uuid)

    transactions = Transaction.objects.filter(uuid=uuid).values()

    return transactions



@api.get("/checkuserbalance")
def check_user_balance(request, checkbalance: CheckBalance, api_key:str):
    user_api_key = get_object_or_404(UserApiKey, key=api_key)
    # check if uuid exists
    uuid =  checkbalance.uuid
    user_wallet = get_object_or_404(UserWallet, uuid=uuid)
    return user_wallet




@api.post("/addfunds")
def add_funds(request, addfunds: AddFunds, api_key:str):
    # if api key doesn't exist it will return 404
    user_api_key = get_object_or_404(UserApiKey, key=api_key)
    # check if uuid exists
    uuid =  addfunds.uuid
    user_wallet = get_object_or_404(UserWallet, uuid=uuid)

    amount = addfunds.uuid

    if amount <= 0:
        return {"error": "Amount must be greater than zero"}

    newbalance = user_wallet.balance + amount

    user_wallet.balance += amount

    user_wallet.save()

    return {"message": f"successfully added {amount} to user account", "new balance": f"{newbalance}"}



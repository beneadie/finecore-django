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
    api_key: str

class RegenApiKey(Schema):
    uuid: str

class CreateUserID(Schema):
    secret_key: str

class AddFunds(Schema):
    amount: int
    uuid: str
    api_key: str

class UserTransactionsGet(Schema):
    uuid: str
    api_key: str


class CheckBalance(Schema):
    uuid: str
    api_key: str


class ListAllTransactions(Schema):
    secret_key: str

class UserWalletCreate(Schema):
    uuid: str  # Foreign key reference to UserApiKey
    secret_key: str

class GetWallets(Schema):
    secret_key: str


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
    try:
        api_model = UserApiKey.objects.create(key=new_key)
        wallet_model = UserWallet.objects.create(uuid=api_model)

    except Exception as e:
        return {"error": str(e)}

    # will row of data in ApiKey table for this UUID
    return {
        "uuid": str(api_model.uuid),  # Convert UUID to string
        "api_key": api_model.key,
        "created_at": api_model.created_at.isoformat(),  # Convert datetime to string
        "balance" : str(wallet_model.balance)

    }



@api.get("/getallwallets")
def getallwallets(request, getwallets: GetWallets):
    if getwallets.secret_key != SECRET_KEY:
        return {"error": "incorrect secret key"}

    wallets = UserWallet.objects.all()
    wallets_data = [{"uuid": str(wallet.uuid), "balance": str(wallet.balance)} for wallet in wallets]


    return wallets_data # Retrieve all wallets





@api.post("/walletcreate")
def create_wallet(request, userwalletcreate: UserWalletCreate):
    if userwalletcreate.secret_key != SECRET_KEY:
        return {"error": "incorrect secret key"}
    try:
        # Retrieve the UserApiKey instance using the provided UUID
        rowUserApiKey = UserApiKey.objects.get(uuid=userwalletcreate.uuid)
        # Create the UserWallet entry with a default balance of 0.0
        user_wallet = UserWallet.objects.create(uuid=rowUserApiKey.uuid, balance=Decimal("0.0"))

        return {
            "uuid": str(user_wallet.uuid.uuid),  # Return UUID as string
            "balance": float(user_wallet.balance)  # Convert Decimal to float for JSON compatibility
        }

    except UserApiKey.DoesNotExist:
        return {"error": "could not create"}




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
            return {
                "uuid": str(user_api_key_row.uuid),  # Convert UUID to string
                "api_key": user_api_key_row.key,
                "created_at": user_api_key_row.created_at.isoformat()  # Convert datetime to string
            }


        except:
            return {"error": "failed to generate and save api key"}, 404

    except UserApiKey.DoesNotExist:
        return {"error": "UserApiKey not found"}, 404



@api.get("/listalltransactions")
def list_transactions(request, listalltransactions : ListAllTransactions):
    if listalltransactions.secret_key != SECRET_KEY:
        return {"error": "incorrect secret key"}
    transactions = Transaction.objects.all()
    print(transactions)
    #return "yes"
    return [
            {
                "uuid": str(transaction.uuid),  # Convert UUID to string
                "api_key": transaction.api_key,
                "description": transaction.description,
                "amount": float(transaction.amount),  # Convert Decimal to float for JSON compatibility
                "datetime": transaction.datetime.isoformat()  # Convert datetime to ISO format
            }
            for transaction in transactions
        ]


# Create a Credit Transaction
@api.post("/createtransaction")
def create_transaction(request, transactioncreditcreate: TransactionCreditCreate):
    # if api key doesn't exist it will return 404
    user_api_key = get_object_or_404(UserApiKey, key=transactioncreditcreate.api_key) # not using this variable

    uuid = transactioncreditcreate.uuid
    user_wallet = get_object_or_404(UserWallet, uuid=uuid)

    description = transactioncreditcreate.description
    amount = transactioncreditcreate.amount
    try:
        transaction = Transaction.objects.create(uuid=uuid, api_key=transactioncreditcreate.api_key, description=description, amount=amount)

        newbalance = user_wallet.balance - amount
        assert newbalance >= 0, f"Insufficient balance: Attempted to withdraw {amount}, but the current balance is {user_wallet.balance}."
        user_wallet.balance -= amount
        user_wallet.save()

        return {"message": f"transactio successful", "new balance": f"{newbalance}"}

    except Exception as e:
        return {"error": str(e)}




@api.get("/getusertransactions")
def add_funds(request, usertransactionsget: UserTransactionsGet):
    # if api key doesn't exist it will return 404
    user_api_key = get_object_or_404(UserApiKey, key=usertransactionsget.api_key)
    # check if uuid exists
    uuid =  usertransactionsget.uuid
    user_wallet = get_object_or_404(UserWallet, uuid=uuid)

    transactions = Transaction.objects.filter(uuid=uuid)
    return [
            {
                "uuid": str(transaction.uuid),  # Convert UUID to string
                "api_key": transaction.api_key,
                "description": transaction.description,
                "amount": float(transaction.amount),  # Convert Decimal to float for JSON compatibility
                "datetime": transaction.datetime.isoformat()  # Convert datetime to ISO format
            }
            for transaction in transactions
        ]





@api.get("/checkuserbalance")
def check_user_balance(request, checkbalance: CheckBalance):
    user_api_key = get_object_or_404(UserApiKey, key=checkbalance.api_key)
    # check if uuid exists
    uuid =  checkbalance.uuid
    user_wallet = get_object_or_404(UserWallet, uuid=uuid)
    return {"balance": user_wallet.balance}




@api.post("/addfunds")
def add_funds(request, addfunds: AddFunds):
    # if api key doesn't exist it will return 404
    user_api_key = get_object_or_404(UserApiKey, key=addfunds.api_key)
    # check if uuid exists
    user_wallet = get_object_or_404(UserWallet, uuid=addfunds.uuid)

    if addfunds.amount <= 0:
        return {"error": "Amount must be greater than zero"}

    newbalance = user_wallet.balance + addfunds.amount

    user_wallet.balance += addfunds.amount

    user_wallet.save()

    return {"message": f"successfully added {addfunds.amount} to user account", "new balance": f"{newbalance}"}



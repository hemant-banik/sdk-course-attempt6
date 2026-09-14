import os
import anthropic
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
config = {"ICA_API_KEY": os.environ.get("ICA_API_KEY")}

print ("SDK Version : " ,anthropic.__version__)

client=Anthropic(
    api_key=config["ICA_API_KEY"],
    base_url="https://api.servicesessentials.ibm.com",
)

print ("Client Type :" , type(client).__name__)

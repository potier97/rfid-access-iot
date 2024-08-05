import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, PutCommand, GetCommand } from "@aws-sdk/lib-dynamodb";

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

export const handler = async (event) => {
  const headers = {
    "Content-Type": "application/json"
  };

  try {
    const { uid, type, thing, group } = event;
    
    console.log("Version 5.0.0");

    if (!uid || !type || !thing || !group) {
      console.log("Invalid input, id and tipo are required");
      return {
        headers,
        statusCode: 400,
        body: JSON.stringify({
          message: "Invalid input, id and tipo are required"
        })
      };
    }

    console.log(`uid: ${uid}, type: ${type}, thing: ${thing}, group: ${group}`);

    const getParams = {
      TableName: process.env.DYNAMODB_TABLE,
      Key: { 
        CardID: uid,
      }
    };

    const getData = await dynamo.send(new GetCommand(getParams));
    if (!getData.Item) {
      return {
        headers,
        statusCode: 409,
        body: JSON.stringify({ message: 'Item does not exist' })
      };
    }


    const params = {
      TableName: process.env.DYNAMODB_TABLE,
      Item: {
        CardID: uid,
        CardType: type,
        EnableCard: false
      }
    };

    await dynamo.send(new PutCommand(params));
    return {
      headers,
      statusCode: 200,
      body: JSON.stringify({ message: "Access card disabled" })
    };
  } catch (error) {
    console.error("Error:", error ? error.message : error);
    return {
      headers,
      statusCode: 500,
      body: JSON.stringify({ message: "Internal Server Error" })
    };
  }
};

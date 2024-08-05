import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, GetCommand } from "@aws-sdk/lib-dynamodb";
import { IoTDataPlaneClient, PublishCommand } from "@aws-sdk/client-iot-data-plane";

const client = new DynamoDBClient({});
const dynamo = DynamoDBDocumentClient.from(client);

const iotClient = new IoTDataPlaneClient({ region: process.env.AWS_REGION });

export const handler = async (event) => {
  const headers = {
    "Content-Type": "application/json"
  };

  try {
    const { uid, type, thing, group, key } = event;
    console.log('Version 5.0.0');

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

    const params = {
      TableName: process.env.DYNAMODB_TABLE,
      Key: {
        CardID: uid
      }
    };

    const data = await dynamo.send(new GetCommand(params));

    if (data.Item && data.Item.EnableCard) {
      const topic = `${thing}/${group}/door/open`;
      const payload = JSON.stringify({ uid, type, thing, group, key });

      const iotParams = {
        topic,
        payload,
        qos: 1 // Quality of Service level
      };
      console.log("Publishing message to topic:", topic);
      await iotClient.send(new PublishCommand(iotParams));
      console.log("Message published");
      return {
        headers,
        statusCode: 200,
        body: JSON.stringify({ message: "Door opened" })
      };
    } else {
      return {
        headers,
        statusCode: 403,
        body: JSON.stringify({ message: "Unauthorized" })
      };
    }
  } catch (error) {
    console.error("Error:", error ? error.message : error);
    return {
      headers,
      statusCode: 500,
      body: JSON.stringify({ message: "Internal Server Error" })
    };
  }
};

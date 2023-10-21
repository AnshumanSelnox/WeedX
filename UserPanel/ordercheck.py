
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd


 

html = '''
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>


<body>

    <div style="height:auto;border:1px solid black;width:100%;">
        <div style="width:100%; height:100%;margin-top: -16px;">
                <p style="margin-left:10px;color:#ffff;padding-top: 10px;">New Order:#{OrderId}</p>


        </div>
        <div style="width: 100%;height:40px;">
            <p style="font-size: 14px; margin-left: 10px;">You have received the following order from {CustomerName}</p>



        </div>
        <div style="width:100%;height:40px;">
            <p style="margin-top: 0px;color: #31B665;margin-left: 10px;">[Order#{OrderId}]({date_str}) </p>



        </div>

            <div style="width:90%;height:auto;margin-left: 10px;">
                <table style="width:100% ;border-spacing:0px;">
                    <tr style="border:1px solid rgb(12, 11, 11)">
                        <th style="text-align:left;border:1px solid rgb(12, 11, 11)">
                            <p style="margin-left: 10px;">Product</p>
                        </th>
                        <th style="text-align:left;border:1px solid rgb(12, 11, 11);width:10%;">
                            <p style="margin-left: 10px;">Quantity</p>
                        </th>
                        <th style="text-align:left;border:1px solid rgb(12, 11, 11)">
                            <p style="margin-left: 10px;">Price $ </p>
                        </th>

                    </tr>
                    <tr style="border:1px solid rgb(12, 11, 11)">
                        <td style="border:1px solid rgb(12, 11, 11)">
                            <p style="margin-left:10px;font-size: 14px;">{ProductName}</p>
                        </td>
                        <td style="border:1px solid rgb(12, 11, 11)">
                            <p style="margin-left:10px;font-size: 14px;">{Quantity}</p>
                        </td>
                        <td style="border:1px solid rgb(12, 11, 11)">
                            <p style="margin-left:10px;font-size: 14px;">{Price}</p>
                        </td>
                    </tr>
                    <tr style="border:1px solid rgb(12, 11, 11)">
                        <td style="border:1px solid rgb(12, 11, 11);" colspan="2">
                            <p style="margin-left:10px;font-size: 14px;">Sub Total</p>
                        </td>
                        <td style="border:1px solid rgb(12, 11, 11)">
                            <p style="margin-left:10px;font-size: 14px;">${subtotal}</p>
                        </td>
                    </tr>
                    <tr style="border:1px solid rgb(12, 11, 11)">
                        <td style="border:1px solid rgb(12, 11, 11)" colspan="2">
                            <p style="margin-left:10px;font-size: 14px;">Shipping</p>
                        </td>
                        <td style="border:1px solid rgb(12, 11, 11)">
                            <p style="margin-left:10px;font-size: 14px;">Free Shipping</p>
                        </td>
                    </tr>
                    <tr style="border:1px solid rgb(12, 11, 11)">
                        <td style="border:1px solid rgb(12, 11, 11)" colspan="2">
                            <p style="margin-left:10px;font-size: 14px;">Payment method</p>
                        </td>
                        <td style="border:1px solid rgb(12, 11, 11)">
                            <p style="margin-left:10px;font-size: 14px;">Cash on delivery</p>
                        </td>
                    </tr>
                    <tr style="border:1px solid rgb(12, 11, 11)">
                        <td style="border:1px solid rgb(12, 11, 11)" colspan="2">
                            <p style="margin-left:10px;font-size: 14px;">Total</p>
                        </td>
                        <td style="border:1px solid rgb(12, 11, 11)">
                            <p style="margin-left:10px;font-size: 14px;">${subtotal}</p>
                        </td>
                    </tr>

                </table>

            </div>


            <div style="width:90%;height:auto;margin-top: 40px;margin-left: 10px;">

                <table style="width:100%;border-spacing:0px;">
                    <tr style="text-align:left;border:1px solid rgb(12, 11, 11)">
                        <th style="text-align:left;border:1px solid rgb(12, 11, 11);padding: 10px;">Billing Address</th>
                        <th style="text-align:left;border:1px solid rgb(12, 11, 11);padding: 10px;">Shipping Address
                        </th>

                    </tr>
                    <tr style="text-align:left;border:1px solid rgb(12, 11, 11)">
                        <td style="text-align:left;border:1px solid rgb(12, 11, 11);font-size: 11px;">
                            <p style="margin-left:10px;font-size: 11px;">
                                {Address}
                            </p>


                        </td>
                        <td style="text-align:left;border:1px solid rgb(12, 11, 11);font-size: 11px;">
                            <p style="margin-left:10px;font-size:11px;">
                               {storeaddress}
                            </p>


                        </td>


                    </tr>
                </table>
            </div>
            <div style="width: 90%;height:30px;">
                <img src={IdCard} alt="Idcard"/>
                <p style="margin-left: 10px;">Congratulations on the sale </p>


            </div>
            <div style="width: 90%;height:30px;margin-bottom: 10px;">
                <p style="margin-top: 0px;margin-left: 10px;">Collect payment easily with our mobile app easily </p>


            </div>
        <div>
        </div>

    </div>



</body>

</html>
    '''

from functools import reduce


def sendmailoforderdetailsVendor(email_to='',OrderId='',subtotal='',ProductName='',Address='',Weight='',Quantity='',Price='',storeaddress='',IdCard='',CustomerName='',Store_Name=''):
    a=[]
    email_from = 'weedxselnox@gmail.com'
    password = 'cbseekrjymhpiydc'
    date_str = pd.Timestamp.today().strftime('%Y-%m-%d')
    email_message = MIMEMultipart()
    email_message['From'] = "WeedX"
    email_message['To']=email_to
    email_message['Subject'] = f'[{Store_Name}] Order Details - {date_str}'
    
    result = reduce(lambda res, l: res + [l[0] + " (" + l[1]+")"], zip(ProductName, Weight), [])
    a="<br>".join(result)
    
    email_message.attach(MIMEText(html.format(OrderId=OrderId,subtotal=subtotal,ProductName=a,Address=Address,Quantity="<br><hr>".join([str(i) for i in Quantity]),Price="<br>".join([str(i) for i in Price]),storeaddress=storeaddress,IdCard=IdCard,date_str=date_str,CustomerName=CustomerName), "html"))
    email_string = email_message.as_string()
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(email_from, password)
        server.sendmail(email_from, email_to, email_string)
        
        
      
      
html1='''
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>


<body>

    <div style="height:auto;border:1px solid black;width:100%;">
        <div style="width:100%; height:100%;margin-top: -16px;">
                <p style="margin-left:10px;"> Hi {CustomerName}, </p>
                <p style="margin-left:10px;">Just to let you know-we've received your order #{OrderId} and it is now being processed</p>






        <div style="width:100%;height:40px;">
            <p style="margin-top: 0px;color: #31B665;margin-left: 10px;">[Order#{OrderId}]({date_str}) </p>



        </div>

            <div style="width:90%;height:auto;margin-left: 10px;">
                <table style="width:100% ;border-spacing:0px;">
                    <tr style="border:1px solid rgb(12, 11, 11)">
                        <th style="text-align:left;border:1px solid rgb(12, 11, 11)">
                            <p style="margin-left: 10px;">Product</p>
                        </th>
                        <th style="text-align:left;border:1px solid rgb(12, 11, 11);width:10%;">
                            <p style="margin-left: 10px;">Quantity</p>
                        </th>
                        <th style="text-align:left;border:1px solid rgb(12, 11, 11)">
                            <p style="margin-left: 10px;">Price $ </p>
                        </th>

                    </tr>
                    <tr style="border:1px solid rgb(12, 11, 11)">
                        <td style="border:1px solid rgb(12, 11, 11)">
                            <p style="margin-left:10px;font-size: 14px;">{ProductName}</p>
                        </td>
                        <td style="border:1px solid rgb(12, 11, 11)">
                            <p style="margin-left:10px;font-size: 14px;">{Quantity}</p>
                        </td>
                        <td style="border:1px solid rgb(12, 11, 11)">
                            <p style="margin-left:10px;font-size: 14px;">{Price}</p>
                        </td>
                    </tr>
                    <tr style="border:1px solid rgb(12, 11, 11)">
                        <td style="border:1px solid rgb(12, 11, 11);" colspan="2">
                            <p style="margin-left:10px;font-size: 14px;">Sub Total</p>
                        </td>
                        <td style="border:1px solid rgb(12, 11, 11)">
                            <p style="margin-left:10px;font-size: 14px;">${subtotal}</p>
                        </td>
                    </tr>
                    <tr style="border:1px solid rgb(12, 11, 11)">
                        <td style="border:1px solid rgb(12, 11, 11)" colspan="2">
                            <p style="margin-left:10px;font-size: 14px;">Shipping</p>
                        </td>
                        <td style="border:1px solid rgb(12, 11, 11)">
                            <p style="margin-left:10px;font-size: 14px;">Free Shipping</p>
                        </td>
                    </tr>
                    <tr style="border:1px solid rgb(12, 11, 11)">
                        <td style="border:1px solid rgb(12, 11, 11)" colspan="2">
                            <p style="margin-left:10px;font-size: 14px;">Payment method</p>
                        </td>
                        <td style="border:1px solid rgb(12, 11, 11)">
                            <p style="margin-left:10px;font-size: 14px;">Cash on delivery</p>
                        </td>
                    </tr>
                    <tr style="border:1px solid rgb(12, 11, 11)">
                        <td style="border:1px solid rgb(12, 11, 11)" colspan="2">
                            <p style="margin-left:10px;font-size: 14px;">Total</p>
                        </td>
                        <td style="border:1px solid rgb(12, 11, 11)">
                            <p style="margin-left:10px;font-size: 14px;">${subtotal}</p>
                        </td>
                    </tr>

                </table>

            </div>


            <div style="width:90%;height:auto;margin-top: 40px;margin-left: 10px;">

                <table style="width:100%;border-spacing:0px;">
                    <tr style="text-align:left;border:1px solid rgb(12, 11, 11)">
                        <th style="text-align:left;border:1px solid rgb(12, 11, 11);padding: 10px;">Billing Address</th>
                        <th style="text-align:left;border:1px solid rgb(12, 11, 11);padding: 10px;">Shipping Address
                        </th>

                    </tr>
                    <tr style="text-align:left;border:1px solid rgb(12, 11, 11)">
                        <td style="text-align:left;border:1px solid rgb(12, 11, 11);font-size: 11px;">
                            <p style="margin-left:10px;font-size: 11px;">
                                {Address}
                            </p>


                        </td>
                        <td style="text-align:left;border:1px solid rgb(12, 11, 11);font-size: 11px;">
                            <p style="margin-left:10px;font-size:11px;">
                               {storeaddress}
                            </p>


                        </td>


                    </tr>
                </table>
            </div>
            <div style="width: 90%;height:30px;">
                <p style="margin-left: 10px;">Congratulations on the sale </p>
            </div>
            <div style="width: 90%;height:30px;margin-bottom: 10px;">
                <p style="margin-top: 0px;margin-left: 10px;">Collect payment easily with our mobile app easily </p>


            </div>
        <div>
        </div>

    </div>



</body>

</html>
'''  
def sendmailoforderdetailsCustomer(email_to='',OrderId='',subtotal='',ProductName='',Address='',Weight='',Quantity='',Price='',storeaddress='',CustomerName=''):
    a=[]
    email_from = 'weedxselnox@gmail.com'
    password = 'cbseekrjymhpiydc'
    date_str = pd.Timestamp.today().strftime('%Y-%m-%d')
    email_message = MIMEMultipart()
    email_message['From'] = "WeedX"
    email_message['To']=email_to
    email_message['Subject'] = f'Order Details - {date_str}'
    
    result = reduce(lambda res, l: res + [l[0] + " (" + l[1]+")"], zip(ProductName, Weight), [])
    a="<br>".join(result)
    
    email_message.attach(MIMEText(html1.format(OrderId=OrderId,subtotal=subtotal,ProductName=a,Address=Address,Quantity="<br><hr>".join([str(i) for i in Quantity]),Price="<br>".join([str(i) for i in Price]),storeaddress=storeaddress,date_str=date_str,CustomerName=CustomerName), "html"))
    email_string = email_message.as_string()
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(email_from, password)
        server.sendmail(email_from, email_to, email_string)

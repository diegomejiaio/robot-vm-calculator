import asyncio
import pandas as pd
from playwright.async_api import async_playwright, expect

def read_config(file_path):
    config = {}
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if '=' in line:
                    name, value = line.strip().split('=')
                    config[name] = value
    except FileNotFoundError:
        print(f"Error: El archivo de configuración '{file_path}' no se encontró.")
    except Exception as e:
        print(f"Error al leer el archivo de configuración: {e}")
    return config

async def main():
    async with async_playwright() as p:
        config = read_config('./config.txt')
        try:
            file_name = config['file_name']
            sheet_name = config['sheet_name']
        except KeyError as e:
            print(f"Error: La clave {e} no se encontró en el archivo de configuración.")
            return
        try:
            excel = pd.read_excel(file_name, sheet_name=sheet_name , header=0)
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            await context.tracing.start(screenshots=True, snapshots=True, sources=True)
            page = await context.new_page()
            await page.set_viewport_size({"width": 1600, "height": 800})
            await page.goto('https://calculator.aws/#/estimate')
            # Change estimation name
            await page.get_by_role("link", name="Edit My Estimate").click()
            await page.get_by_placeholder("Enter Name").click()
            await page.get_by_placeholder("Enter Name").fill("J2C UEAN V5")
            await page.get_by_label("Save", exact=True).click()
            await page.get_by_label("Add service").first.click()
            for _, row in excel.iterrows():
                await page.get_by_placeholder("Search for a service").click()
                await page.get_by_placeholder("Search for a service").fill("ec2")
                await page.get_by_label("Configure Amazon EC2").click()
                await page.get_by_placeholder("Enter a description for your estimate").click()
                # Add EC2 instance name
                await page.get_by_placeholder("Enter a description for your estimate").fill(row['instance_name'])
                await page.get_by_placeholder("Enter a description for your estimate").press("Enter")
                await page.get_by_label("Choose a Region").click()
                # select region
                await page.get_by_role("combobox").fill(row['region'])
                await page.get_by_text(str(row['region']), exact=True).click()
                # select operating system

                match row.ope_system:
                    case "windows":
                        await page.get_by_label("Operating system").click()
                        ## await page.get_by_title("Windows Server", exact=True).locator("span").nth(1).click()
                        await page.get_by_role("option", name="Windows Server", exact=True).click()
                        await page.get_by_label("Operating system").press("Escape")
                ## await page.pause()
                # select instance type
                await page.get_by_placeholder("Search by instance name or filter by keyword").click()
                await page.get_by_placeholder("Search by instance name or filter by keyword").fill(row['instance_family'])
                await page.get_by_role("table", name="EC2 selection").get_by_label("").check()
                await page.get_by_role("button", name="Other purchasing options").click()
                match row.payment_type:
                    case "On-Demand":
                        await page.get_by_label("On-Demand", exact=True).check()
                        await page.get_by_label("Usage", exact=True).click()
                        await page.get_by_label("Usage", exact=True).fill(str(row['monthly_usage']))
                    case "Compute Savings Plans":
                        match row.reserved_years:
                            case 1:
                                await page.locator("[id=\"compute-savings-1\\ Year\"]").check()
                            case 3:
                                await page.locator("[id=\"compute-savings-3\\ Year\"]").check()
                        match row.payment_option:
                            case "No Upfront":
                                await page.locator("#compute-savings-None").check()
                            case "Partial Upfront":
                                await page.locator("#compute-savings-Partial").check()
                            case "All Upfront":
                                await page.locator("#compute-savings-All").check()
                    case "EC2 Instance Savings Plans":
                        await page.get_by_text("EC2 Instance Savings PlansGet deeper discount when you only need one instance fa").click()
                        # Get the radio button element
                        radio_button = page.get_by_label("EC2 Instance Savings Plans")

                        # Click the radio button if it's not already checked
                        if not await radio_button.is_checked():
                            await radio_button.click()
                        match row.reserved_years:
                            case 1:
                                await page.locator("[id=\"instance-savings-1\\ Year\"]").check()
                            case 3:
                                await page.locator("[id=\"instance-savings-3\\ Year\"]").check()
                        match row.payment_option:
                            case "No Upfront":
                                await page.locator("#instance-savings-None").check()
                            case "Partial Upfront":
                                await page.locator("#instance-savings-Partial").check()
                            case "All Upfront":
                                await page.locator("#instance-savings-All").check()
                    case "Convertible Reserved Instances":
                        await page.get_by_label("Convertible Reserved Instances", exact=True).check()
                        match row.reserved_years:
                            case 1:
                                await page.locator("[id=\"convertible-1\\ Year\"]").check()
                            case 3:
                                await page.locator("[id=\"convertible-3\\ Year\"]").check()
                        match row.payment_option:
                            case "No Upfront":
                                await page.locator("#convertible-None").check()
                            case "Partial Upfront":
                                await page.locator("#convertible-Partial").check()
                            case "All Upfront":
                                await page.locator("#convertible-All").check()
                    case "Standard Reserved Instances":
                        await page.get_by_label("Standard Reserved Instances").check()
                        match row.reserved_years:
                            case 1:
                                await page.locator("[id=\"standard-1\\ Year\"]").check()
                            case 3:
                                await page.locator("[id=\"standard-3\\ Year\"]").check()
                        match row.payment_option:
                            case "No Upfront":
                                await page.locator("#standard-None").check()
                            case "Partial Upfront":
                                await page.locator("#standard-Partial").check()
                            case "All Upfront":
                                await page.locator("#standard-All").check()
                    case _:
                        await page.get_by_label("Standard Reserved Instances").check()
                # select term type
                await page.get_by_role("button", name="Amazon Elastic Block Store (EBS) - optional Amazon Elastic Block Store (EBS) Info").click()
                await page.get_by_label("Storage amount Value").click()
                # select storage amount
                await page.get_by_label("Storage amount Value").fill(str(row['ebs_storage']))
                await page.get_by_label("Snapshot Frequency").click()
                # select snapshot frequency
                await page.get_by_role("option", name=str(row['snapshot_freq']),exact=True).click()
                # select amount changed per snapshot
                if str(row['snapshot_freq']) != "No snapshot storage":
                    await page.get_by_label("Amount changed per snapshot Value").click()
                    await page.get_by_label("Amount changed per snapshot Value").fill(str(row['snapshot_storage']))
                else:
                    pass
                # next row 
                await page.get_by_role("button", name="Save and add service").click()
                # verify if the service was added
                assert await page.get_by_text('Successfully added Amazon EC2 estimate.').is_visible()
            await page.get_by_role("button", name="View summary").click()

            await page.click('text="Share"')
            await page.click('text="Agree and continue"')

            # Wait 5 seconds
            await page.wait_for_timeout(5000)
            # Copy public link
            await page.get_by_role("button", name="Copy public link").click()
            await context.tracing.stop(path="logs/trace.zip")
            await page.pause()
        except Exception as e:
            await context.tracing.stop(path="logs/trace.zip")
            print(f"Error durante la ejecución de Playwright: {e}")
            await asyncio.sleep(300)  # Mantiene la ventana abierta por 300 segundos para inspección

        # browser.close()


asyncio.run(main())
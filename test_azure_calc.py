import asyncio
import pandas as pd
from playwright.async_api import async_playwright


# Función para leer la configuración desde un archivo
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

# Función para validar los datos de una fila
def validate_row(row, valid_values):
    for field, valid_options in valid_values.items():
        if row[field] not in valid_options:
            raise ValueError(f"Invalid value '{row[field]}' for field '{field}'.")

async def main():
    async with async_playwright() as p:
        config = read_config('./config.txt')
        
        try:
            file_name = config['file_name']
            sheet_name = config['sheet_name']
        except KeyError as e:
            print(f"Error: La clave {e} no se encontró en el archivo de configuración.")
            return

        valid_values = {
            'ope_system': ['Linux', 'Windows'],
            'os_type': [
                'Ubuntu', 'Red Hat Enterprise Linux', 'SUSE Linux Enterprise', 'Ubuntu Pro', 
                'RHEL for SAP Business Applications', 'RHEL for SAP with HA', 
                'SQL Server Ubuntu Linux', 'SQL Server Ubuntu Pro', 
                'SQL Server Red Hat Enterprise Linux', 'SQL Server SUSE Priority', 
                'SUSE Linux Enterprise for HPC', 'SUSE Linux Enterprise for SAP Applications + 24x7 Support', 
                'Ubuntu Advantage', '(OS Only)', 'BizTalk', 'SQL Server'
            ],
            'payment_type': ['Pay as you go', '1 year reserved', '3 year reserved'],
            'license_type': ['License included', 'Azure Hybrid Benefit'],
            'disk_tier': ['Standard HDD', 'Standard SSD'],
            'disk_size': list(range(32, 32768 + 1, 32))
        }

        excel = pd.read_excel(file_name, sheet_name=sheet_name, header=0)

        user_profile_path = "/Users/diegomejia/Library/Application Support/Google/Chrome"

        # Lanzar Chrome con el perfil de usuario existente
        browser = await p.chromium.launch_persistent_context(
            user_profile_path,
            headless=False,
            channel='chrome'  # Asegura que se use Google Chrome en lugar de Chromium
        )

        # Abre una nueva página
        page = await browser.new_page()

    
        # Navega a la página deseada
        await page.goto('https://azure.microsoft.com/en-us/pricing/calculator/')
        await page.wait_for_load_state('networkidle')

        try:
            await page.locator('#lp-proactive-invite').evaluate('node => node.remove()')
        except Exception as e:
            print("No se encontró el popup de chat o no pudo ser cerrado.")

        for i, row in excel.iterrows():
            try:
                validate_row(row, valid_values)

                # Add a new VM to the estimate
                await page.get_by_label("Popular").get_by_test_id("virtual-machines-picker-item").click()

                # Wait for the VM configuration section to be visible
                await page.wait_for_selector('.products-holder .wa-calcService[data-testid="virtual-machines-module"]', state='visible')

                # Get all VM configurations, ensuring we select the last one
                vm_config = page.locator('.products-holder .wa-calcService[data-testid="virtual-machines-module"]').last
                await vm_config.wait_for(state='visible')
                await vm_config.locator('input[name="displayName"]').fill(str(i+1))
                # Configure the VM
                if row['ope_system'].lower() == 'windows':
                    await vm_config.locator('select[aria-label="Operating system"]').select_option("windows")
                elif row['ope_system'].lower() == 'linux':
                    await vm_config.locator('select[aria-label="Operating system"]').select_option("linux")
                if row['os_type'] == "Red Hat Enterprise Linux":
                    await vm_config.locator('select[aria-label="Type"]').select_option("redhat")

                # Select VM size
                await vm_config.locator('.instancesSearchDropdown__control').click()
                await vm_config.locator('.instancesSearchDropdown__input').fill(row['instance_name'])
                await vm_config.locator('.instancesSearchDropdown__input').press("Enter")

                # Select payment type
                if row['payment_type'] == '1 year reserved':
                    await vm_config.locator('text=/^1 year reserved /').click()
                elif row['payment_type'] == '3 year reserved':
                    await vm_config.locator('text=/^3 year reserved /').click()

                if row['license_type'] == 'Azure Hybrid Benefit':
                    await vm_config.locator('text="Azure Hybrid Benefit"').click()
                # si es redhat, licencia incluida y reservada por un año, entonces marca el radiobutton
                if row['os_type'] == 'Red Hat Enterprise Linux' and row['license_type'] == 'License included' and row['payment_type'] == '1 year reserved':
                    await vm_config.get_by_label("1 year reserved", exact=True).check()
                    print("cumple con la condición")
                # Configure disk
                await vm_config.locator('text="Managed Disks"').click()
                
                if row['disk_tier'] == "Standard HDD":
                    match row.disk_size:
                        case 32:
                            await vm_config.locator('select[aria-label="Disk size"]').select_option("s4")
                        case 64:
                            await vm_config.locator('select[aria-label="Disk size"]').select_option("s6")
                        case 128:
                            await vm_config.locator('select[aria-label="Disk size"]').select_option("s10")
                        case 256:
                            await vm_config.locator('select[aria-label="Disk size"]').select_option("s15")
                        case 512:
                            await vm_config.locator('select[aria-label="Disk size"]').select_option("s20")
                        case 1024:
                            await vm_config.locator('select[aria-label="Disk size"]').select_option("s30")
                        case 2048:
                            await vm_config.locator('select[aria-label="Disk size"]').select_option("s40")
                        case 4096:
                            await vm_config.locator('select[aria-label="Disk size"]').select_option("s50")
                        case 8192:
                            await vm_config.locator('select[aria-label="Disk size"]').select_option("s60")
                        case 16384:
                            await vm_config.locator('select[aria-label="Disk size"]').select_option("s70")
                        case 32768:
                            await vm_config.locator('select[aria-label="Disk size"]').select_option("s80")
                        case _:
                            await vm_config.locator('select[aria-label="Disk size"]').select_option("s4")

                elif row['disk_tier'] == "Standard SSD":
                    await vm_config.locator('select[name="managedDiskTier"]').select_option("standardssd")
                    match row.disk_size:
                        case 4:
                            await vm_config.locator('select[aria-label="Disk size"]').select_option("e1")
                        case 8:
                            await vm_config.locator('select[aria-label="Disk size"]').select_option("e2")
                        case 16:
                            await vm_config.locator('select[aria-label="Disk size"]').select_option("e3")
                        case 32:
                            await vm_config.locator('select[aria-label="Disk size"]').select_option("e4")
                        case 64:
                            await vm_config.locator('select[aria-label="Disk size"]').select_option("e6")
                        case 128:
                            await vm_config.locator('select[aria-label="Disk size"]').select_option("e10")
                        case 256:
                            await vm_config.locator('select[aria-label="Disk size"]').select_option("e15")
                        case 512:
                            await vm_config.locator('select[aria-label="Disk size"]').select_option("e20")
                        case 1024:
                            await vm_config.locator('select[aria-label="Disk size"]').select_option("e30")
                        case 2048:
                            await vm_config.locator('select[aria-label="Disk size"]').select_option("e40")
                        case 4096:
                            await vm_config.locator('select[aria-label="Disk size"]').select_option("e50")
                        case 8192:
                            await vm_config.locator('select[aria-label="Disk size"]').select_option("e60")
                        case 16384:
                            await vm_config.locator('select[aria-label="Disk size"]').select_option("e70")
                        case 32768:
                            await vm_config.locator('select[aria-label="Disk size"]').select_option("e80")
                        case _:
                            await vm_config.locator('select[aria-label="Disk size"]').select_option("e1")

                if int(row['disk_size']) > 0:
                    await vm_config.locator('input[aria-label="Disks"]').fill("1")
                
                # incluir nombre en <input class="text-input" type="text" name="displayName" placeholder="Virtual Machines" aria-label="product-name" value="">
                

                print(f"Configuración completada para la máquina {row['instance_name']} de la iteracion {i+1}")

            except ValueError as e:
                print(f"Error: {e}")
                await page.pause()

            await asyncio.sleep(1)

        await page.pause()

        await browser.close()

asyncio.run(main())

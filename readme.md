# Robot VM Pricing

This project automates the process of calculating the cost of virtual machine instances on both AWS EC2 and Azure, using Playwright and Python.

## Demo (Spanish)

[![Watch Loom Video](https://cdn.loom.com/sessions/thumbnails/1ecaba2f486740248db39099a01459d2-with-play.gif)](https://www.loom.com/share/1ecaba2f486740248db39099a01459d2)

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Support

### Payment Types

- AWS:
  - On-Demand
  - Convertible Reserved Instances
  - Standard Reserved Instances
  - Compute Savings Plans
  - EC2 Instance Savings Plans
- Azure:
  - Pay as you go
  - 1 year reserved
  - 3 year reserved

### Operating Systems

- AWS:
  - Linux
  - Windows
- Azure:
  - Ubuntu
  - Red Hat Enterprise Linux
  - SUSE Linux Enterprise
  - Ubuntu Pro
  - SQL Server
  - Others (see details in the code)

## Installation

1. Install [Playwright](https://playwright.dev/python/docs/intro)
2. Clone the repository:
   ```bash
   git clone https://github.com/diegomejiaio/robot-vm-calculator
   ```
3. Navigate to the project directory:
   ```bash
      cd robot-vm-calculator
   ```
4. Create a virtual environment:
   ```bash
      python -m venv env
   ```
5. Activate the virtual environment:
   - For Windows:
      ```bash
         .\env\Scripts\activate
      ```
   - For macOS/Linux:
      ```bash
         source venv/bin/activate
      ```
6. Install the required packages:
   ```bash
         pip install -r requirements.txt
   ```
## Usage

### AWS
1. Use `pricing-ec2.xlsx` as a template.
2. Define your own Excel file.
3. Use config.txt to define your data source.
4. Run:
   ```bash
         pytest test_aws_calc.py
   ```
### Azure
1. Use `pricing-azure-template.xlsx` as a template.
2. Define your own Excel file.
3. Use config.txt to define your data source.
4. Run:
   ```bash
      pytest test_azure_calc.py
   ```





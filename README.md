## ERPNext Australian Localisation :

The ERPNext Australian Localisation app will install the necessary localisation functionalities for Australian business in ERPNext. This app works in line with the Australian Chart of Accounts. The features of this app are as follows: 
1. Assist the Australian companies to get the GST postings based on the Supplier and Customer type (Local / International / Capital Goods / Non Capital Goods). 
2. Generate the BAS report with the amounts to be reported in each of the BAS Label (1A, 1B, G1 to G9 and G10 to G20). 
3. Payment Proposal functionality to match the Payment Run for local suppliers.
4. Generate ABA (Specified by Australian Banking Association) file used to process electronic transactions for supplier payments through the internet banking system of Australian banks.

### Prerequisites

ERPNext v15.74.0 or above

### Installation

The AU Localisation app for ERPNext can be installed using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/Arus-Info/ERPNext-Australian-Localisation.git
bench install-app erpnext_australian_localisation
```

<img width="1325" height="889" alt="image" src="https://github.com/user-attachments/assets/920d9787-9af0-4345-b79a-a5759104d7d1" />

### Features

* Capital Goods & Non Capital Goods Supplier definition in the Supplier Master's Tax Category field
* Import Supplier definition in the Supplier Master's Tax Category field
* Domestic / Export Customer definition in the Customer Master's Tax Category field
* Exempt Item definition in the Item Master's Tax tab
* Sales amounts are reported in G1, G2 and G3 as per the Customer Tax Category definition
* Purchase amounts are reported in G10, G11 and G14 as per the Supplier Tax Category definition
* Input Taxed Sales and the corresponding Purchase recording to report in G4 and G13 BAS Labels
* Estimated Purchase for Private Use recording to report in G15 BAS Label
* Adjustments for Sales and Purchase to report in G7 and G18 BAS Labels
* The final 1A and 1B label amounts will be reported to arrive at the amount business needs to pay the ATO or the amount ATO will refund the business
* BAS reports can be generated Monthly / Quarterly
* BAS reports (detailed information with transactional document number) can be printed in PDF format
* Payment Proposal (Batch) generation for Supplier Payment
* ABA File generation for the Payment Batch which can be used to upload into the online banking system for bulk payments for the suppliers

### Screenshots & Setup Instructions

When the new company is created, please select the chart of Accounts template "Australia - Chart of Accounts with Account Numbers".

<img width="914" height="796" alt="image" src="https://github.com/user-attachments/assets/145de6ce-befc-43aa-9bde-0d2c00c81cff" />

For additional / new Australian companies in the existing system

<img width="1388" height="381" alt="image" src="https://github.com/user-attachments/assets/e467265c-56e7-4637-bc43-d49f8b73d3a3" />
<br><br>
Australian Localiation Workspace - Carries the basic instructions & the functionalities offered
<br><br>
<img width="1322" height="900" alt="image" src="https://github.com/user-attachments/assets/a458a04d-d954-4a3d-92a6-f4edebafd619" />
<br><br>
<img width="1342" height="867" alt="image" src="https://github.com/user-attachments/assets/c3618678-4b1c-443d-ab6c-59d84e390e61" />
<br><br>
<ins>AU Localisation Settings:</ins> The frequency of BAS report submission can be changed from Monthly to Quarterly only when there is no open BAS report is available in the system
<br><br>
<img width="1332" height="360" alt="image" src="https://github.com/user-attachments/assets/6cab65ea-c20b-4544-bec2-dccf386c708a" />
<br><br>
<ins>Glimpse of the BAS Report:</ins>
<br><br>
<img width="1344" height="889" alt="image" src="https://github.com/user-attachments/assets/6d17466e-3175-4f65-a91a-6c200cbaefa8" />
<br><br>
<img width="1346" height="889" alt="image" src="https://github.com/user-attachments/assets/8751e178-512d-4ee2-85d6-b36da3a1e54d" />
<br><br>
Printable format of the BAS Report - Please print in Landspcape orientation for better readability
<br><br>
<img width="1373" height="884" alt="image" src="https://github.com/user-attachments/assets/3383ce0a-ab45-49b9-98f7-c7ba6f58aea7" />
<br><br>
<img width="1322" height="955" alt="image" src="https://github.com/user-attachments/assets/8949e8de-a925-4793-a5f4-952fa983c0c6" />
<br><br>
<ins>Setup for ABA file generation:</ins>
<br><br>
Company Bank Account Setup - Below information are mandatory for ABA file generation
<br><br>
<img width="1390" height="625" alt="image" src="https://github.com/user-attachments/assets/6ad410fc-d559-455a-a308-4339d535f633" />
<img width="1313" height="616" alt="image" src="https://github.com/user-attachments/assets/04b97a3f-a441-4ae7-93f5-face25067046" />
<br><br>
For every suppliers where ABA file needs to be generated, the below information are mandatory. The Lodgement Reference entered on the supplier master comes as default reference in the Payment Batch. But this can be overriden in the Payment batch.
<br><br>
<img width="1395" height="787" alt="image" src="https://github.com/user-attachments/assets/032a9b59-bc85-4aef-944a-b36a471f4aea" />
<br><br>
Payment Proposal Functionality: This functionality is equivalent to Payment Run process to generate bulk payments. This functionality allows the user to filter the Invoices based on Due Date & the Invoice created User.
<br><br>
<img width="1400" height="853" alt="image" src="https://github.com/user-attachments/assets/dddf8465-5a69-47fe-b878-caf31bab383a" />
<br><br>
<img width="1349" height="897" alt="image" src="https://github.com/user-attachments/assets/1590fd44-c7d1-4bd8-9b73-67fa784cd9ee" />
<br><br>
Alternate option of creating a Payment Batch without using Payment Proposal functionality: Using this functionality, the Payment Batch is manually created and the Payments which are in Draft status can be pulled into the Payment Batch for ABA file generation.
<br><br>
<img width="1375" height="344" alt="image" src="https://github.com/user-attachments/assets/a7aad0be-aaf3-40b2-bf32-0645c5cfbc84" />
<br><br>
<img width="1346" height="849" alt="image" src="https://github.com/user-attachments/assets/7de041ca-9a98-4894-ae55-dce4ba51e005" />
<br><br>
ABA File generation functionality from the Payment Batch screen:
<br><br>
<img width="1461" height="840" alt="image" src="https://github.com/user-attachments/assets/ba0eab43-769d-4389-8863-e232b7449474" />
<br><br>


### License

This project is licensed under GNU General Public License (v3)

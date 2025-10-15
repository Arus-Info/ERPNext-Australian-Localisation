## ERPNext Australian Localisation :

The ERPNext Australian Localisation app will install the necessary localisation functionalities for Australian business in ERPNext. This app works in line with the Australian Chart of Accounts. The features of this app are as follows:

1. Assist the Australian companies to get the GST postings based on the Supplier and Customer type (Local / International / Capital Goods / Non Capital Goods).
2. Options for the companies to choose the method for BAS Reporting - Full reporting or Simpler Reporting.
3. Generate the BAS report based on Full Reporting method with the amounts to be reported in each of the BAS Label (1A, 1B, G1 to G9 and G10 to G20).
4. Generate the BAS report based on Simpler Reporting method with the amounts to be reported in each of the BAS Label (1A, 1B and G1).
5. Payment Proposal functionality to match the Payment Run for local suppliers.
6. Generate ABA (Specified by Australian Banking Association) file used to process electronic transactions for supplier payments through the internet banking system of Australian banks.

### Prerequisites

ERPNext v15.74.0 or above

### Installation

The AU Localisation app for ERPNext can be installed using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/Arus-Info/ERPNext-Australian-Localisation.git --branch version-15
bench install-app erpnext_australian_localisation
```
<img width="1620" height="870" alt="image" src="https://github.com/user-attachments/assets/c4c9056b-3ca9-4933-ba13-9e63b2547d40" />

### Features

- BAS Report can be generated based on either Simpler or Full reporting method
- Capital Goods & Non Capital Goods Supplier definition in the Supplier Master's Tax Category field
- Import Supplier definition in the Supplier Master's Tax Category field
- Domestic / Export Customer definition in the Customer Master's Tax Category field
- Exempt Item definition in the Item Master's Tax tab
- ### Full BAS Reporting Method:
  - Sales amounts are reported in G1, G2 and G3 as per the Customer Tax Category definition
  - Purchase amounts are reported in G10, G11 and G14 as per the Supplier Tax Category definition
  - Input Taxed Sales and the corresponding Purchase recording to report in G4 and G13 BAS Labels
  - Estimated Purchase for Private Use recording to report in G15 BAS Label
  - Adjustments for Sales and Purchase to report in G7 and G18 BAS Labels
- ### Simpler BAS Reporting Method:
  - Sales amounts are reported in G1 based on GL Entries.
- The final 1A and 1B label amounts will be reported to arrive at the amount business needs to pay the ATO or the amount ATO will refund the business
- BAS reports can be generated Monthly / Quarterly
- BAS reports (detailed information with transactional document number) can be printed in PDF format
- Payment Proposal (Batch) generation for Supplier / Employee Payment
- ABA File generation for the Payment Batch which can be used to upload into the online banking system for bulk payments for the suppliers / employees

### Screenshots & Setup Instructions

When the new company is created, please select the chart of Accounts template "Australia - Chart of Accounts with Account Numbers".

<img width="914" height="796" alt="image" src="https://github.com/user-attachments/assets/145de6ce-befc-43aa-9bde-0d2c00c81cff" />

For additional / new Australian companies in the existing system

<img width="1388" height="381" alt="image" src="https://github.com/user-attachments/assets/e467265c-56e7-4637-bc43-d49f8b73d3a3" />
<br><br>
Australian Localiation Workspace - Carries the basic instructions & the functionalities offered
<br><br>
<img width="1612" height="869" alt="image" src="https://github.com/user-attachments/assets/4fbb1c1e-94fe-4d27-8b11-130cd90c3b87" />
<br><br>
<img width="1618" height="865" alt="image" src="https://github.com/user-attachments/assets/34046ce9-6ba9-4c9b-bb6e-a3632ce3184f" />
<br><br>
<ins>AU Localisation Settings:</ins> The frequency of BAS report submission can be changed from Monthly to Quarterly only when there is no open BAS report is available in the system. Also the BAS Reporting Method (Full/Simpler) is defined on the below page.
<br><br>
<img width="1636" height="499" alt="image" src="https://github.com/user-attachments/assets/94de5c70-d96e-4e44-9f27-a3a2cfafb9cb" />
<br><br>
In case of Simpler BAS Reporting method to be used, the Account setup for BAS labels are available in Simpler BAS Report Setup.
<br><br>
<img width="1719" height="676" alt="image" src="https://github.com/user-attachments/assets/f23eba75-4b09-4696-84e2-5df64ce21545" />
<br><br>
<ins>Glimpse of the BAS Report:</ins>
<br><br>

**Simpler BAS Report**
<br><br>
<img width="1639" height="832" alt="image" src="https://github.com/user-attachments/assets/6944f69a-0c48-4ad5-83bc-f74796afc6c0" />
<br><br>

**Full BAS Report**
<br><br>
<img width="1344" height="889" alt="image" src="https://github.com/user-attachments/assets/6d17466e-3175-4f65-a91a-6c200cbaefa8" />
<br><br>
<img width="1346" height="889" alt="image" src="https://github.com/user-attachments/assets/8751e178-512d-4ee2-85d6-b36da3a1e54d" />
<br><br>
Printable format of the BAS Report - Please print in Landspcape orientation for better readability
<br><br>
<img width="1648" height="858" alt="image" src="https://github.com/user-attachments/assets/0caef4f3-91e2-4ee6-9ff6-457b4f00ec5a" />
<br><br>
<img width="1231" height="731" alt="image" src="https://github.com/user-attachments/assets/d5f8dedd-a621-48cb-b74a-386f6e048d8e" />
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
<ins>Payment Proposal Functionality</ins>: This functionality is equivalent to Payment Run process to generate bulk payments. This functionality allows the user to filter the documents based on Due / Posting Date & the document created User.
<br><br>
<img width="1670" height="816" alt="image" src="https://github.com/user-attachments/assets/80bf62b1-7c00-4b48-83aa-84fcd1d761b5" />
<br><br>
<img width="1512" height="873" alt="image" src="https://github.com/user-attachments/assets/dc3033df-3aa1-48f3-9b07-534a5b4a48cd" />
<br><br>
Alternate option of creating a Payment Batch without using Payment Proposal functionality: Using this functionality, the Payment Batch is manually created and the Payments which are in Draft status can be pulled into the Payment Batch for ABA file generation.
<br><br>
<img width="1479" height="400" alt="image" src="https://github.com/user-attachments/assets/b2f7deea-5585-4c01-9fd8-065bac2065d8" />
<br><br>
<img width="1540" height="869" alt="image" src="https://github.com/user-attachments/assets/a9626cf1-8826-4f87-85d6-e26d4e68befa" />
<br><br>
ABA File generation functionality from the Payment Batch screen:
<br><br>
<img width="1520" height="882" alt="image" src="https://github.com/user-attachments/assets/7ca8c0ec-305a-44e1-936c-1737582bb392" />
<br><br>

### License

This project is licensed under GNU General Public License (v3)

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

<img width="1299" height="901" alt="image" src="https://github.com/user-attachments/assets/7fec5b5a-9abe-4b63-996a-da54f5c4aaf9" />

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

### Screenshots

When the new company is created, please select the chart of Accounts template "Australia - Chart of Accounts with Account Numbers".

![select chart of accounts](image-2.png)

For additional / new Australian companies in the existing system

![select chart of accounts2](image-1.png)

<img width="1358" height="894" alt="image" src="https://github.com/user-attachments/assets/a305c7f0-e730-45b9-98e3-a569940b8c9e" />

<img width="1332" height="360" alt="image" src="https://github.com/user-attachments/assets/6cab65ea-c20b-4544-bec2-dccf386c708a" />

<img width="1344" height="889" alt="image" src="https://github.com/user-attachments/assets/6d17466e-3175-4f65-a91a-6c200cbaefa8" />

<img width="1346" height="889" alt="image" src="https://github.com/user-attachments/assets/8751e178-512d-4ee2-85d6-b36da3a1e54d" />

<img width="1373" height="884" alt="image" src="https://github.com/user-attachments/assets/3383ce0a-ab45-49b9-98f7-c7ba6f58aea7" />

<img width="1322" height="955" alt="image" src="https://github.com/user-attachments/assets/8949e8de-a925-4793-a5f4-952fa983c0c6" />







### License

This project is licensed under GNU General Public License (v3)

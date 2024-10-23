# Pwned_tool - Check Your Emails and Passwords

[中文][url-doczh]

## Introduction

​	A Python3-based tool for detecting email and password breaches, supporting batch detection. It uses `haveibeenbreached` to verify email leaks without the need for official paid APIs! Password verification uses the API of the `haveibeenpwned` website.

​	The password verification uses the API of the `haveibeenpwned` (haveibeenpwned.com) website, which employs a "k-anonymity" algorithm model. The strength of this algorithm lies in the fact that it only requires the first 5 characters of the password hash sequence, not the entire password, to search for breaches without submitting the full plaintext password. **This means your plaintext password is not uploaded to the network for detection!**

The algorithm implementation is as follows:

![image](assets/image-20241023125855-224z3pw.png)

## Features

* **Batch Detection**: Capable of detecting multiple emails or passwords for breaches at the same time.
* **No API Needed**: Directly usable without registration or requesting official APIs.
* **Easy to Use**: Simple command-line interface for easy operation.
* **Python Implementation**: Written in Python, cross-platform compatible.

## Usage

Prerequisite: **Use** **`python3`** **version to run**

1. **Download the Project**:

```
git clone https://github.com/AgonySec/pwned_tool
```

2. **Configure Dependencies**:

   Ensure Python environment is installed. Then install the required dependencies via pip:

```go

pip3 install -r requirements.txt
```

3. **Run the Tool**:  
   Execute the script via command line and pass the file containing the emails or passwords you want to test:

```python
python pwned_tool.py
usage: pwned_tool.py [-h] [-e EMAIL] [-f FILE] [-p PASSWORD] [-pf PASSFILE]

options:
  -h, --help            show this help message and exit
  -e EMAIL, --email EMAIL
                        Input the email address to test
  -f FILE, --file FILE  Input the file path containing multiple email addresses
  -p PASSWORD, --password PASSWORD
                        Input the password to test
  -pf PASSFILE, --passFile PASSFILE
                        Input the file path containing multiple passwords

```

## Examples

### Testing a Single Email

```go
python pwned_tool.py -e tom@gmail.com
```

The response results are stored in the corresponding file in the `result` directory:

![image-20241023165545888](assets/image-20241023165545888.png)

### Testing a Single Password

```go
python pwned_tool.py -p admin123
```

![image-20241023165938499](assets/image-20241023165938499.png)

### Batch Testing Emails

Assuming you have a list file `emails.txt` containing email addresses, one per line.

![image-20241023170013659](assets/image-20241023170013659.png)

Run the following command to test:

```go
python pwned_tool.py -f emails.txt
```

![image-20241023170104073](assets/image-20241023170104073.png)

The detection results are stored in `DataBreachEmailsLog.txt` in the current directory:

![image-20241023170259496](assets/image-20241023170259496.png)

The response results are stored in the corresponding file in the `result` directory:

![image-20241023170338048](assets/image-20241023170338048.png)

### Batch Testing Passwords

```go
python pwned_tool.py -pf pass.txt
```

![image-20241023170510626](assets/image-20241023170510626.png)

The detection results are stored in `DataBreachPasswordsLog.txt` in the current directory:

![image-20241023170716082](assets/image-20241023170716082.png)

## Note

It is necessary to clarify that **the logic for detecting password breaches here is actually comparing the password you input with publicly leaked intelligence. If they match, it is considered a password breach! It has nothing to do with the email account being tested!**

## Contributing

Contributions to this project are welcome. If you find any issues or have suggestions for new features, please submit them via GitHub Issues.

## License

This project is licensed under the [MIT License](LICENSE).

---

Thank you for using pwned_tool!

---

Please note that the images referenced in the document will need to be translated to their English file names or paths if they are to be used in an English context.

[url-doczh]: README.md
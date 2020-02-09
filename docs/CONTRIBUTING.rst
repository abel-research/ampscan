Contributing 
============

Hey everyone! Thanks for taking time to contribute, we want to ensure ampscan is a collaborative project within the P&O community and we really appreciate your input. 

Before you contribute to the repo, please discuss your prospective change with a member of the core team. We can be contacted via email, twitter or on GitHub. We want to ensure ampscan has a clear focus for the P&O community and can be used by those who are not software experts.  

We also have a [code of conduct](CODE_OF_CONDUCT.md), please follow it in any interactions within the project. 


Reporting issues
----------------

- **Search for existing issues.** Please check to see if someone else has reported the same issue.
- **Share as much information as possible.** Include operating system and version, browser, version and any screenshots. Also, include steps to reproduce the bug.

Project Setup
-------------
Refer to the [README](README.md).

Code Style
----------

Testing
-------
Testing is performed automatically using [Travis Ci](https://travis-ci.org/abel-research/ampscan). New tests can be added to the repo using the python unittest module with in the tests folder. 

Pull requests
-------------
- Try not to pollute your pull request with unintended changes – keep them simple and small. If possible, squash your commits.
- Try to share how your code has been tested before submitting a pull request.
- If your PR resolves an issue, include **closes #ISSUE_NUMBER** in your commit message (or a [synonym](https://help.github.com/articles/closing-issues-via-commit-messages)).
- Review
    - If your PR is ready for review, another contributor will be assigned to review your PR
    - The reviewer will accept or comment on the PR. 
    - If needed address the comments left by the reviewer. Once you're ready to continue the review, ping the reviewer in a comment.
    - Once accepted your code will be merged to `master`

Documentation
-------------
Documentation for the ampscan library is automatically generated using 
[sphinx](http://www.sphinx-doc.org/en/master/). Any additional code should be documented in 
accordance with 'numpy style' docstrings. A template can be found 
[here](https://www.numpy.org/devdocs/docs/howto_document.html#example).
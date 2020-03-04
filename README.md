# floodgame_norms
This application allows to use the Floodgame as an oTree application in three languages with several treatments. The experiment was conducted in October 2019 among 605 Spanish homeowners and in August 2019 with 1200 Dutch homeowners. By uncommenting several lines in the code, you can run the game in different languages and/or run different treatments.  

To install the app to your local oTree directory, copy the folder 'floodgame_norms' to your oTree Django project and extend the session configurations in your ```settings.py``` at the root of the oTree directory:

```
SESSION_CONFIGS = [
    dict(
        name='floodgame_norms_en',
        display_name="Floodgame norms",
        num_demo_participants=1,
        app_sequence=['floodgame_norms'],
        quota_baseline=1,
        quota_baseline_1=1,
        quota_norm_all=1,
        quota_norm_high=1,
        quota_norm_focusing=1,
        quota_norm_focusing_1=1,
        demo=False,
        language='en'
    )
                  ]
```

## Treatments
* baseline 
(no social norm nudge, belief elicitation stage áfter own decision)
* baseline_1 
(same as baseline, but added descriptive norm nudge in final page to measure information search)
* norm_focusing 
(norm focusing through belief elicitation stage before own decision)
* norm_focusing_1 
(same as norm_focusing, but added descriptive norm nudge in final page to measure information search)
* norm_all 
(transparent social norm nudge, showing percentages of previous investments)
* norm_high
(binary social norm nudge, highlighting percentage of previous investors)


## Languages
* English 
* Dutch (through Django localization file)
* Spanish (through Django localization file)

Note that the understanding questions rely on [otree-utils](https://github.com/WZBSocialScienceCenter/otreeutils). 

## Issues
Localization was not stable for the *UnderstandingQuestionsPage*, which is why the questions have been translated manually. This issue should be solved if one wants to conduct an experiment simultaneously in two countries. 

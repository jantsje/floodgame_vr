# floodgame_vr
This application uses the control treatment of the floodgame. It was developed for use in the VR lab and has a question about presence and simulator sickness. After the flood belief questions, participants will reach a page where they are notified that the VR experience is about to start. To advance participants to the next page, click 'advance slowest user to the next page' at the 'Monitor' tab. 

To install the app to your local oTree directory, copy the folder 'floodgame_vr' to your oTree Django project and extend the session configurations in your ```settings.py``` at the root of the oTree directory:

```
SESSION_CONFIGS = [
    dict(
        name='floodgame_vr',
        display_name="Floodgame for VR",
        num_demo_participants=1,
        app_sequence=['floodgame_vr'],
        demo=False,
        language='nl'
    )
                  ]
```

## Languages
* English 
* Dutch (through Django localization file)

Note that the understanding questions rely on [otree-utils](https://github.com/WZBSocialScienceCenter/otreeutils). 

## Issues
Localization was not stable for the *UnderstandingQuestionsPage*, which is why the questions have been translated manually. This issue should be solved if one wants to conduct an experiment simultaneously in two countries. 

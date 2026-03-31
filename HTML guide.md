# Login selection page

```html
<button _ngcontent-ng-c1484386674="" mat-raised-button="" color="accent" id="sacButton" class="mdc-button mat-mdc-button-base externalProvider_button mdc-button--raised mat-mdc-raised-button mat-accent" mat-ripple-loader-class-name="mat-mdc-button-ripple"><span class="mat-mdc-button-persistent-ripple mdc-button__ripple"></span><span class="mdc-button__label"> Continuer avec compte CAS </span><span class="mat-focus-indicator"></span><span class="mat-mdc-button-touch-target"></span><span class="mat-ripple mat-mdc-button-ripple"></span></button>
```

# Login page
```html
<div id="page">
<div class="container-fluid">
<div id="page-header">
</div>
<div class="sheet current"><div class="container-shadow"><div id="content"><div class="content-header">
<h1>
Se connecter avec SAC/CAS-Portal
</h1>
</div>
<div id="flash">

</div>
<div class="fields-separation">
<div class="oauth-application-logo">
<img src="/packs/media/images/oauth_app_thumb-5f4cadc5cf206bf2905ee9876ed3a3e7.png" width="64" height="64">
</div>
<p>
Veuillez vous connecter sur hut-reservation.orgpour continuer.
</p>
<hr>
</div>

<br>
<div class="row flex-column-reverse">
<div class="col-md-12">
<form data-turbo="false" class="new_person" id="new_person" action="/fr/users/sign_in?oauth=true" accept-charset="UTF-8" method="post"><input type="hidden" name="authenticity_token" value="AMKJCG7bdZiqQx2F9pKfdPxzCIp_qEza-QOlSinPfR7wpVo2-_GSvlWRs44SQQwO3wNKSuZFeF-NvClmkCMaYA" autocomplete="off">
<div class="row mb-2"><label class="col-md-3 col-xl-2 col-form-label text-md-end pb-1" for="person_login_identity">E-mail ou N° de membre</label><div class="labeled col-md-9 col-lg-8 col-xl-8 mw-63ch" style=""><input autocomplete="login" autofocus="autofocus" class="mw-100 mw-md-60ch form-control form-control-sm mw-100 mw-md-60ch" type="text" name="person[login_identity]" id="person_login_identity" style=""></div></div>
<div class="row mb-2"><label class="col-md-3 col-xl-2 col-form-label text-md-end pb-1" for="person_password">Mot de passe</label><div class="labeled col-md-9 col-lg-8 col-xl-8 mw-63ch"><div class="position-relative" data-controller="password-toggle"><input class="form-control form-control-sm mw-100 mw-md-60ch pe-5" data-password-toggle-target="input" type="password" name="person[password]" id="person_password"><button type="button" class="position-absolute end-0 top-50 translate-middle-y me-2 text-muted password-toggle btn-link bg-transparent me-0" data-action="click-&gt;password-toggle#toggle"><i class="fa-regular fa-eye" data-password-toggle-target="icon"></i></button></div></div></div>
<div class="row mb-2"><label class="col-md-3 col-xl-2 col-form-label text-md-end pb-1" for="person_remember_me">Se souvenir de moi</label><div class="labeled col-md-9 col-lg-8 col-xl-8 mw-63ch"><div class="form-check"><input name="person[remember_me]" type="hidden" value="0" autocomplete="off"><input class="form-check-input" type="checkbox" value="1" name="person[remember_me]" id="person_remember_me"><label class="form-check-label me-2" for="person_remember_me"> </label></div></div></div>
<div class="row mb-2"><div class="offset-md-3 offset-xl-2 col-md-9 col-xl-10"><div class="btn-group"><button name="button" type="submit" class="btn btn-sm btn-primary mt-2" data-turbo-submits-with="Inscription">Inscription</button></div></div></div>
<div class="row mb-2"><div class="offset-md-3 offset-xl-2 col-md-9 col-xl-10"><div class="m-0">
<a href="/fr/users/password/new">Mot de passe oublié?</a>
<span class="hide-last">
|
</span>
<a href="/fr/users/confirmation/new">Pas reçu de message de confirmation&nbsp;?</a>
</div>
<div class="m-0">
<a href="/fr/groups/8/self_registration">Tu n'ês pas membre du CAS? Ouvre dès maintenant ton compte du CAS gratuit.</a>
<span class="hide-last">
|
</span>
<a href="https://www.sac-cas.ch/fr/affiliation/devenir-membre/">Demander l'adhésion au CAS</a>
</div>

</div></div></form></div>
<div class="col-md-12">
<div class="contactable well">
<address>
<strong>SAC-CAS</strong>

<p>Monbijoustrasse 61<br>3007 Bern</p>





</address>
<div class="social">

</div>


</div>

</div>
</div>


</div></div></div></div>
</div>
```

## The field username
```html
<input autocomplete="login" autofocus="autofocus" class="mw-100 mw-md-60ch form-control form-control-sm mw-100 mw-md-60ch" type="text" name="person[login_identity]" id="person_login_identity" style="">
```

## The field password
```html
<input class="form-control form-control-sm mw-100 mw-md-60ch pe-5" data-password-toggle-target="input" type="password" name="person[password]" id="person_password">
```

# The home page with hut new booking button
```html
<button _ngcontent-ng-c2799991326="" color="accent" mat-raised-button="" class="mdc-button mat-mdc-button-base reservation_list__mat-raised-button-green add_button mdc-button--raised mat-mdc-raised-button mat-accent" mat-ripple-loader-class-name="mat-mdc-button-ripple"><span class="mat-mdc-button-persistent-ripple mdc-button__ripple"></span><span class="mdc-button__label"> NOUVELLE RÉSERVATION </span><span class="mat-focus-indicator"></span><span class="mat-mdc-button-touch-target"></span><span class="mat-ripple mat-mdc-button-ripple"></span></button>
```

# The hut selection popup
```html
<div class="mat-mdc-text-field-wrapper mdc-text-field mdc-text-field--outlined mdc-text-field--no-label"><!----><div class="mat-mdc-form-field-flex"><div matformfieldnotchedoutline="" class="mdc-notched-outline mdc-notched-outline--no-label"><div class="mat-mdc-notch-piece mdc-notched-outline__leading"></div><div class="mat-mdc-notch-piece mdc-notched-outline__notch"><!----><!----><!----></div><div class="mat-mdc-notch-piece mdc-notched-outline__trailing"></div></div><!----><!----><!----><div class="mat-mdc-form-field-infix"><!----><input _ngcontent-ng-c523414532="" matinput="" id="hutInput" class="mat-mdc-input-element mat-mdc-autocomplete-trigger mat-mdc-form-field-input-control mdc-text-field__input ng-pristine ng-valid cdk-text-field-autofill-monitored ng-touched" placeholder="Sélectionner cabane" aria-invalid="false" aria-required="false" autocomplete="off" role="combobox" aria-autocomplete="list" aria-expanded="true" aria-haspopup="listbox" aria-controls="mat-autocomplete-0"><!----><mat-autocomplete _ngcontent-ng-c523414532="" class="mat-mdc-autocomplete"><!----></mat-autocomplete></div><!----><!----></div><!----></div>
```

## The ok button
```html
<button _ngcontent-ng-c523414532="" mat-dialog-close="" mat-raised-button="" color="accent" class="mdc-button mat-mdc-button-base modal_wrapper__mat-raised-button-green mdc-button--raised mat-mdc-raised-button mat-accent" mat-ripple-loader-class-name="mat-mdc-button-ripple" type="button"><span class="mat-mdc-button-persistent-ripple mdc-button__ripple"></span><span class="mdc-button__label"> OK </span><span class="mat-focus-indicator"></span><span class="mat-mdc-button-touch-target"></span><span class="mat-ripple mat-mdc-button-ripple"></span></button>
```

# The booking page
## The date selector
```html
<app-date-picker _ngcontent-ng-c3196813188=""><form novalidate="" class="form_main ng-pristine ng-invalid ng-touched"><mat-form-field subscriptsizing="dynamic" class="mat-mdc-form-field date_picker mat-mdc-form-field-type-mat-date-range-input mat-mdc-form-field-has-icon-suffix mat-form-field-appearance-outline mat-primary mat-form-field-animations-enabled mat-form-field-hide-placeholder"><!----><div class="mat-mdc-text-field-wrapper mdc-text-field mdc-text-field--outlined"><!----><div class="mat-mdc-form-field-flex"><div matformfieldnotchedoutline="" class="mdc-notched-outline mdc-notched-outline--upgraded"><div class="mat-mdc-notch-piece mdc-notched-outline__leading"></div><div class="mat-mdc-notch-piece mdc-notched-outline__notch" style=""><label matformfieldfloatinglabel="" class="mdc-floating-label mat-mdc-floating-label" id="mat-mdc-form-field-label-5" style=""><mat-label id="formlabel" data-test="label-date-from-to-reservation" class="date_range" aria-label="Date du - au"> Date du - au <span aria-hidden="true" style="margin-left: -0.125rem;">*</span></mat-label><!----></label><!----><!----><!----></div><div class="mat-mdc-notch-piece mdc-notched-outline__trailing"></div></div><!----><!----><!----><div class="mat-mdc-form-field-infix"><!----><mat-date-range-input role="group" class="mat-date-range-input mat-mdc-input-element mat-mdc-form-field-input-control mdc-text-field__input" id="mat-date-range-input-1" aria-labelledby="mat-mdc-form-field-label-5" data-mat-calendar="mat-datepicker-1"><div cdkmonitorsubtreefocus="" class="mat-date-range-input-container"><div class="mat-date-range-input-wrapper"><input type="text" matstartdate="" id="cy-arrivalDate__input" formcontrolname="arrivalDate" aria-required="true" data-test="input-arrival-date-reservation" autocomplete="off" class="mat-start-date mat-date-range-input-inner ng-pristine ng-valid ng-touched" placeholder="De" aria-haspopup="dialog"><span aria-hidden="true" class="mat-date-range-input-mirror">De</span></div><span class="mat-date-range-input-separator mat-date-range-input-separator-hidden">–</span><div class="mat-date-range-input-wrapper mat-date-range-input-end-wrapper"><input type="text" matenddate="" formcontrolname="departureDate" aria-required="true" data-test="input-departure-date-reservation" autocomplete="off" class="mat-end-date mat-date-range-input-inner ng-untouched ng-pristine ng-valid" placeholder="à" aria-haspopup="dialog"><span aria-hidden="true" class="mat-date-range-input-mirror">à</span></div></div></mat-date-range-input><mat-date-range-picker></mat-date-range-picker><!----></div><!----><div class="mat-mdc-form-field-icon-suffix"><mat-datepicker-toggle id="cy-datePicker__toggle" maticonsuffix="" class="mat-datepicker-toggle" data-mat-calendar="mat-datepicker-1"><button maticonbutton="" type="button" class="mdc-icon-button mat-mdc-icon-button mat-mdc-button-base mat-unthemed" mat-ripple-loader-class-name="mat-mdc-button-ripple" mat-ripple-loader-centered="" aria-haspopup="dialog" aria-label="Open calendar" aria-expanded="false" tabindex="0"><span class="mat-mdc-button-persistent-ripple mdc-icon-button__ripple"></span><svg viewBox="0 0 24 24" width="24px" height="24px" fill="currentColor" focusable="false" aria-hidden="true" class="mat-datepicker-toggle-default-icon"><path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z"></path></svg><!----><span class="mat-focus-indicator"></span><span class="mat-mdc-button-touch-target"></span><span class="mat-ripple mat-mdc-button-ripple"></span></button></mat-datepicker-toggle></div><!----></div><!----></div><div aria-atomic="true" aria-live="polite" class="mat-mdc-form-field-subscript-wrapper mat-mdc-form-field-bottom-align mat-mdc-form-field-subscript-dynamic-size"><!----><div class="mat-mdc-form-field-hint-wrapper"><!----><div class="mat-mdc-form-field-hint-spacer"></div></div><!----></div></mat-form-field><div aria-live="assertive" aria-atomic="true" id="dateRangeErrors" class="errorContainer"><!----><!----><!----><!----></div></form></app-date-picker>
```

## The availability view after entering date
```html
<div _ngcontent-ng-c3196813188="" class="rightColumn"><!----><app-availability-table _ngcontent-ng-c3196813188="" _nghost-ng-c1299497831=""><div _ngcontent-ng-c1299497831="" class="dateTab"><table _ngcontent-ng-c1299497831="" aria-label="Date Availability Table" mat-table="" class="mat-mdc-table mdc-data-table__table cdk-table table" role="table"><!----><thead role="rowgroup"><mat-header-row _ngcontent-ng-c1299497831="" role="row" class="mat-mdc-header-row mdc-data-table__header-row cdk-header-row"><th _ngcontent-ng-c1299497831="" role="columnheader" mat-header-cell="" class="mat-mdc-header-cell mdc-data-table__header-cell cdk-header-cell tab_header_date cdk-column-date mat-column-date"> Date </th><th _ngcontent-ng-c1299497831="" role="columnheader" mat-header-cell="" class="mat-mdc-header-cell mdc-data-table__header-cell cdk-header-cell tab_header_places cdk-column-freePlaces mat-column-freePlaces"> Places disponibles </th><th _ngcontent-ng-c1299497831="" role="columnheader" mat-header-cell="" scope="row" class="mat-mdc-header-cell mdc-data-table__header-cell cdk-header-cell tab_header_chevron cdk-column-expand mat-column-expand" aria-label="Informations complementaires"></th><!----></mat-header-row><!----></thead><tbody role="rowgroup" class="mdc-data-table__content"><mat-row _ngcontent-ng-c1299497831="" role="row" tabindex="0" class="mat-mdc-row mdc-data-table__row cdk-row" aria-expanded="true" aria-controls="details-undefined" aria-label="Samedi 11 Avril 2026. 0 places libres"><td _ngcontent-ng-c1299497831="" mat-cell="" tabindex="0" class="mat-mdc-cell mdc-data-table__cell cdk-cell table_row_date cdk-column-date mat-column-date" role="cell" aria-label="Samedi 11 Avril 2026"><span _ngcontent-ng-c1299497831="" role="img" class="icon" aria-label="Disponible à la réservation"></span><!----><!----><div _ngcontent-ng-c1299497831="" class="calendarDate"><span _ngcontent-ng-c1299497831=""> Sam </span><span _ngcontent-ng-c1299497831=""> 11.04.2026 </span></div></td><td _ngcontent-ng-c1299497831="" tabindex="0" mat-cell="" class="mat-mdc-cell mdc-data-table__cell cdk-cell table_row_places cdk-column-freePlaces mat-column-freePlaces" role="cell" aria-label="0 places libres"> 0 <span _ngcontent-ng-c1299497831="" aria-hidden="true" class="icon_exclamation" style="visibility: hidden;"> ! </span></td><td _ngcontent-ng-c1299497831="" mat-cell="" aria-label="expand column" class="mat-mdc-cell mdc-data-table__cell cdk-cell table_row_chevron cdk-column-expand mat-column-expand" role="cell"><button _ngcontent-ng-c1299497831="" aria-label="expand row" mat-icon-button="" class="mdc-icon-button mat-mdc-icon-button mat-mdc-button-base mat-unthemed" mat-ripple-loader-uninitialized="" mat-ripple-loader-class-name="mat-mdc-button-ripple" mat-ripple-loader-centered=""><span class="mat-mdc-button-persistent-ripple mdc-icon-button__ripple"></span><mat-icon _ngcontent-ng-c1299497831="" role="img" class="mat-icon notranslate material-icons mat-ligature-font mat-icon-no-color" aria-hidden="true" data-mat-icon-type="font"> keyboard_arrow_up </mat-icon><span class="mat-focus-indicator"></span><span class="mat-mdc-button-touch-target"></span></button></td><!----></mat-row><mat-row _ngcontent-ng-c1299497831="" role="row" class="mat-mdc-row mdc-data-table__row cdk-row"><td _ngcontent-ng-c1299497831="" mat-cell="" class="mat-mdc-cell mdc-data-table__cell cdk-cell expand_row cdk-column-details mat-column-details" role="cell" colspan="3"><div _ngcontent-ng-c1299497831="" class="expandable_row expanded"><div _ngcontent-ng-c1299497831="" class="expansion_content"><div _ngcontent-ng-c1299497831="" class="text_content"><div _ngcontent-ng-c1299497831="" class="date_details"><div _ngcontent-ng-c1299497831="" role="group" tabindex="0" class="label_freePlaces"><div _ngcontent-ng-c1299497831="" class="total_places"><div _ngcontent-ng-c1299497831="" class="category_details"><div _ngcontent-ng-c1299497831="" class="room_disponibility_icon"><!----><div _ngcontent-ng-c1299497831="" class="icon icon_circle" aria-label="Non disponible à la réservation"><svg _ngcontent-ng-c1299497831="" fill="none" height="24" width="24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><circle _ngcontent-ng-c1299497831="" cx="7" cy="11.25" fill="#d70000" r="6.85"></circle></svg></div><!----></div><span _ngcontent-ng-c1299497831="" class="label">Dortoir:</span></div><div _ngcontent-ng-c1299497831="" class="numberOfPlacesContainer"><div _ngcontent-ng-c1299497831="" class="numberOfPlaces"><span _ngcontent-ng-c1299497831="" class="totalFreePlaces"> 0 </span><span _ngcontent-ng-c1299497831="" aria-hidden="true" class="icon_exclamation" style="visibility: hidden;"> ! </span></div></div></div></div><!----></div><!----></div><!----></div><!----></div></td><!----></mat-row><!----><!----></tbody><tfoot role="rowgroup" class="mat-mdc-table-sticky" style="display: none; bottom: 0px; z-index: 10;"><!----></tfoot><!----><!----></table></div><!----></app-availability-table></div>
```
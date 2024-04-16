flectra.define('point_of_sale.tour.ReceiptScreenTourMethods',function(require){
    'usestrict';

    const{createTourMethods}=require('point_of_sale.tour.utils');

    classDo{
        clickNextOrder(){
            return[
                {
                    content:'gotonextscreen',
                    trigger:'.receipt-screen.button.next.highlight',
                },
            ];
        }
        setEmail(email){
            return[
                {
                    trigger:'.receipt-screen.input-emailinput',
                    run:`text${email}`,
                },
            ];
        }
        clickSend(isHighlighted=true){
            return[
                {
                    trigger:`.receipt-screen.input-email.send${isHighlighted?'.highlight':''}`,
                },
            ];
        }
    }

    classCheck{
        isShown(){
            return[
                {
                    content:'receiptscreenisshown',
                    trigger:'.pos.receipt-screen',
                    run:()=>{},
                },
            ];
        }

        receiptIsThere(){
            return[
                {
                    content:'thereshouldbethereceipt',
                    trigger:'.receipt-screen.pos-receipt',
                    run:()=>{},
                },
            ];
        }

        totalAmountContains(value){
            return[
                {
                    trigger:`.receipt-screen.top-contenth1:contains("${value}")`,
                    run:()=>{},
                },
            ];
        }

        emailIsSuccessful(){
            return[
                {
                    trigger:`.receipt-screen.notice.successful`,
                    run:()=>{},
                },
            ];
        }
        discountAmountIs(value){
            return[
                {
                    trigger:`.pos-receipt>div:contains("Discounts")>span:contains("${value}")`,
                    run:()=>{},
                },
            ];
        }
    }

    classExecute{
        nextOrder(){
            return[...this._check.isShown(),...this._do.clickNextOrder()];
        }
    }

    returncreateTourMethods('ReceiptScreen',Do,Check,Execute);
});

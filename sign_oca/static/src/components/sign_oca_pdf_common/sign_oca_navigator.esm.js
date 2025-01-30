/** @odoo-module QWeb **/
/* global document, window, console */
import {_t} from "@web/core/l10n/translation";

export function offset(el) {
    const box = el.getBoundingClientRect();
    const docElem = document.documentElement;
    return {
        top: box.top + window.scrollY - docElem.clientTop,
        left: box.left + window.scrollY - docElem.clientLeft,
    };
}

/**
 * Starts the sign item navigator
 * @param { SignablePDFIframe } parent
 * @param { HTMLElement } target
 * @param { Object } types
 * @param { Environment } env
 */
export function startSignItemNavigator(parent, target, types, env) {
    console.log("types", types);
    console.log("env", env);

    const state = {
        started: false,
        isScrolling: false,
    };

    const navigator = document.createElement("div");
    navigator.classList.add("o_sign_sign_item_navigator");
    const navLine = document.createElement("div");
    navLine.classList.add("o_sign_sign_item_navline");

    // Function _scrollToSignItemPromise(item) {
    //     if (env.isSmall) {
    //         return new Promise((resolve) => {
    //             state.isScrolling = true;
    //             item.scrollIntoView({
    //                 behavior: "smooth",
    //                 block: "center",
    //                 inline: "center",
    //             });
    //             resolve();
    //         });
    //     }
    //     State.isScrolling = true;
    //     const viewer = parent.iframe.el.contentDocument.getElementById("viewer");
    //     const containerHeight = target.offsetHeight;
    //     const viewerHeight = viewer.offsetHeight;

    //     const scrollOffset = containerHeight / 4;
    //     Const scrollTop = offset(item).top - offset(viewer).top - scrollOffset;
    //     if (scrollTop + containerHeight > viewerHeight) {
    //         scrollOffset += scrollTop + containerHeight - viewerHeight;
    //     }
    //     if (scrollTop < 0) {
    //         scrollOffset += scrollTop;
    //     }
    //     scrollOffset +=
    //         offset(target).top -
    //         navigator.offsetHeight / 2 +
    //         item.getBoundingClientRect().height / 2;

    //     const duration = Math.max(
    //         Math.min(
    //             500,
    //             5 *
    //                 (Math.abs(target.scrollTop - scrollTop) +
    //                     Math.abs(navigator.getBoundingClientRect().top) -
    //                     scrollOffset)
    //         ),
    //         100
    //     );

    //     return new Promise((resolve) => {
    //         target.scrollTo({top: scrollTop, behavior: "smooth"});
    //         target.scrollTo({behavior: "smooth"});
    //         const an = navigator.animate(
    //             {top: `${scrollOffset}px`},
    //             {duration, fill: "forwards"}
    //         );
    //         const an2 = navLine.animate(
    //             {top: `${scrollOffset}px`},
    //             {duration, fill: "forwards"}
    //         );
    //         Promise.all([an.finished, an2.finished]).then(() => resolve());
    //     });

    //     return new Promise((resolve, reject) => {
    //         setTimeout(() => {
    //             resolve("Promise resolved! ✅");
    //         }, 2000); // Simulates an async task
    //     });
    // }

    function setTip(text) {
        navigator.style.fontFamily = "Helvetica";
        navigator.innerText = text;
    }

    // /**
    //  * Sets the entire radio set on focus.
    //  * @param {Number} radio_set_id
    //  */
    // function highligtRadioSet(radio_set_id) {
    //     parent
    //         .checkSignItemsCompletion()
    //         .filter((item) => item.data.radio_set_id === radio_set_id)
    //         .forEach((item) => {
    //             item.el.classList.add("ui-selected");
    //         });
    // }

    function scrollToSignItem({el: item, data}) {
        console.log("item", item);
        console.log("data", data);

        // _scrollToSignItemPromise(item).then(() => {
        //     Const type = types[data.type_id];
        //     if (type.item_type === "text" && item.querySelector("input")) {
        //         item.value = item.querySelector("input").value;
        //         item.focus = () => item.querySelector("input").focus();
        //     }
        //     // Maybe store signature in data rather than in the dataset
        //     if (item.value === "" && !item.dataset.signature) {
        //         setTip(type.tip);
        //     }
        //     // parent.refreshSignItems();
        //     if (data.type === "radio") {
        //         // We need to highligt the entire radio set items
        //         highligtRadioSet(data.radio_set_id);
        //     } else {
        //         item.focus();
        //         item.classList.add("ui-selected");
        //     }
        //     if (["signature", "initial"].includes(type.item_type)) {
        //         if (item.dataset.hasFocus) {
        //             const clickableElement = data.isSignItemEditable
        //                 ? item.querySelector(".o_sign_item_display")
        //                 : item;
        //             clickableElement.click();
        //         } else {
        //             item.dataset.hasFocus = true;
        //         }
        //     }
        //     state.isScrolling = false;
        // });
    }

    function goToNextSignItem() {
        if (!state.started) {
            state.started = true;
            // Parent.refreshSignItems();
            goToNextSignItem();
            return false;
        }
        const selectedElements = target.querySelectorAll(".ui-selected");
        selectedElements.forEach((selectedElement) => {
            selectedElement.classList.remove("ui-selected");
        });

        // I am using this function to return all fields to be signed
        // but in EE it returns an array of objects
        const signItemsToComplete2 = parent.checkSignItemsCompletion().sort((a, b) => {
            return (
                100 * (a.data.page - b.data.page) +
                10 * (a.data.posY - b.data.posY) +
                (a.data.posX - b.data.posX)
            );
        });
        const signItemsToComplete = [
            {data: {page: 1, posY: 10, posX: 20}},
            {data: {page: 2, posY: 5, posX: 30}},
            {data: {page: 1, posY: 15, posX: 25}},
        ];

        if (signItemsToComplete.length > 0) {
            const first_target_field = signItemsToComplete2[0][0];

            console.log("first_target_field", typeof first_target_field);
            console.log("first_target_field", first_target_field);

            scrollToSignItem(signItemsToComplete[0]);
            first_target_field.append(navigator);
        }
    }

    navigator.addEventListener("click", goToNextSignItem);

    goToNextSignItem();
    // Target.append(navigator);
    navigator.before(navLine);

    setTip(_t("Click to start"));
    navigator.focus();

    function toggle(force) {
        navigator.style.display = force ? "" : "none";
        navLine.style.display = force ? "" : "none";
    }

    return {
        setTip,
        goToNextSignItem,
        toggle,
        state,
    };
}

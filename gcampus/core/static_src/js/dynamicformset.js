import Collapse from 'bootstrap/js/src/collapse';


const TEMPLATE_POSTFIX = 'EMPTY_FORM_TEMPLATE';


class DynamicFormset {
    /**
     * Dynamic Formset
     *
     * @param formsetID {String}: Identifier for the formset. Used in
     *      HTML IDs, etc. Usually equates to ``{{ formset.prefix }}``
     */
    constructor(formsetID) {
        this.formsetID = formsetID;
        this.prefixID = `id_${this.formsetID}`;
        this.template = this.getByID(TEMPLATE_POSTFIX).innerHTML;
        this.addButton = this.getByID('ADD');
        this.addButton.addEventListener('click', this.addForm.bind(this));
        this.totalFormCountInput = this.getByID('TOTAL_FORMS');
        for (let i = 0; i < this.totalFormCount; i++) {
            this.registerDeleteButton(i);
        }
    }

    /**
     * Get By ID
     *
     * Get element with ``postfix`` by ID. Can be used for formset
     * specific fields (such as ``TOTAL_FORMS``) when ``index`` is not
     * set, or for form specific fields such as ``DELETE`` if a form
     * index is provided.
     *
     * @param postfix {String}: Ending of the id, e.g. ``ADD``.
     * @param index {Number}: Number of the form. Can be left blank if
     *      not form specific.
     * @returns {HTMLElement}
     */
    getByID(postfix, index= null) {
        if (index === undefined || index === null) {
            return document.getElementById(`${this.prefixID}-${postfix}`);
        } else {
            return document.getElementById(
                `${this.prefixID}-${index}-${postfix}`
            );
        }
    }

    get totalFormCount() {
        let value = this.totalFormCountInput.value;
        try {
            return Number.parseInt(value);
        } catch (e) {
            throw new Error(`Invalid value for TOTAL_FORMS: ${value}`);
        }
    }

    set totalFormCount(value) {
        this.totalFormCountInput.value = value;
    }

    registerDeleteButton(index) {
        let button = this.getByID('DELETE-button', index);
        button.addEventListener('click', () => {
            this.delete(index);
        });
    }

    /**
     * Check if form entry is new, i.e. the entry has not yet been
     * written to the database. In the case of it being new, it was
     * added using JavaScript and can thus be removed from the DOM.
     * If however the form was already written to the database and
     * should now be deleted, it has to be hidden from the user and a
     * flag has to be set in order to delete it.
     *
     * @param index - Number: Integer indicating the number of the form
     */
    isFormNew(index) {
        let entryID = this.getByID('id', index);
        if (entryID.value === undefined || entryID.value === '') {
            return true;
        } else {
            try {
                Number.parseInt(entryID.value);
                return false;
            } catch {
                return true;
            }
        }
    }

    delete(index) {
        let formElement = this.getByID('FORM', index);
        formElement.classList.add('collapse', 'show');
        let collapse = new Collapse(formElement, {toggle: false});
        collapse.hide();
        formElement.addEventListener('hidden.bs.collapse', () => {
            if (this.isFormNew(index)) {
                // Form is new (i.e. created by JavaScript) and can be
                // removed safely.
                formElement.remove();
                this.totalFormCount--;  // Decrement number of forms
            } else {
                // Form was initially created by the backand and is thus
                // already in the database. It can not be deleted by
                // removing the element.
                formElement.classList.add('d-none');  // Hide element
                let deleteFlag = this.getByID('DELETE', index);

                deleteFlag.value = 1;
            }
        });

    }

    addForm() {
        let formNumber = this.totalFormCount;
        let newForm = this.template.replace(/__prefix__/g, String(formNumber));
        if (formNumber > 0) {
            let previousElement = this.getByID('FORM', formNumber - 1);
            previousElement.insertAdjacentHTML('afterend', newForm);
        } else {
            let parent = this.getByID('FORM-CONTAINER');
            parent.insertAdjacentHTML('afterbegin', newForm);
        }
        // Find newly created element and immanently trigger collapse
        let newElement = this.getByID('FORM', formNumber);
        let collapse = new Collapse(newElement, {trigger: true});
        // Add button event listener
        this.registerDeleteButton(formNumber);
        this.totalFormCount++;
    }
}


export {DynamicFormset};

/**
 * Basic utiltiy functions for this application.
 * 
 * @author LeStarch
 */

/**
 * Check list equivalent via element ID field or element equivalence
 * 
 * Check equivalence between two lists. May use "id" to esablish identity of sub-objects. Otherwise
 * compares lists directly. When the elements of the list cannot be compared directly, accuracy
 * depends on an identity key.
 * 
 * @param {Array} list_a: first list to compare 
 * @param {Array} list_b: second list to compare
 * @param {string} id: object key used as identity
 * @returns {boolean}: true when equal, false when likely not equal  
 */
export function compareList(list_a, list_b, id) {
    // Check length first for quick non-equality
    if (list_a.length != list_b.length) {
        return false;
    }
    // Check each element using id key, or when not set, fallback to direct equivalence
    for (let i = 0; i < list_a.length; i++) {
        if (( id && (list_a[i][id] != list_b[i][id])) ||
            (!id && (list_a[i] != list_b[i]))) {
            return false;
        }
    }
    return true;
}

/**
 * Update a list in-place when the current data is different from the new data
 * 
 * Update a list with new items in-place iff the lists are not equivalent. When id is set then it
 * is used as the id-key for checking equivalence as descrived in the 'compareList' function.
 * 
 * Note: the purpose of this method is to modify oritinal list, it may be modified. This is done
 * for data binding integrity as the original list object reference is maintained throughout.
 * 
 * @param {Array} original_list: original list to be set to new items
 * @param {Array} new_list: new list to populate original list
 * @param {string} id: object key used as identity (passed to compareList)
 */
export function setListInPlace(original_list, new_list, id) {
    if (!compareList(original_list, new_list, id)) {
        original_list.splice(0, original_list.length, ...new_list);
    }
}
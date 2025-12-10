/**
 * NetSuite RESTlet for Top 40 Dashboard Data
 * 
 * This RESTlet should be deployed in NetSuite to handle data requests
 * from the Streamlit dashboard.
 * 
 * Deployment Instructions:
 * 1. Save this file in NetSuite File Cabinet
 * 2. Create new Script Record (RESTlet type)
 * 3. Deploy to appropriate role/users
 * 4. Note the generated RESTlet URL
 * 5. Update the URL in netsuite_connector.py
 * 
 * @NApiVersion 2.1
 * @NScriptType Restlet
 */

define(['N/search', 'N/record', 'N/format'], function(search, record, format) {
    
    /**
     * POST handler - main entry point
     */
    function post(requestBody) {
        try {
            var action = requestBody.action;
            
            switch(action) {
                case 'test_connection':
                    return testConnection();
                    
                case 'get_sales_transactions':
                    return getSalesTransactions(requestBody);
                    
                case 'get_item_master':
                    return getItemMaster(requestBody);
                    
                case 'get_customer_master':
                    return getCustomerMaster(requestBody);
                    
                case 'execute_saved_search':
                    return executeSavedSearch(requestBody);
                    
                case 'get_cost_retail_data':
                    return getCostRetailData(requestBody);
                    
                default:
                    return {
                        status: 'error',
                        message: 'Unknown action: ' + action
                    };
            }
        } catch(e) {
            return {
                status: 'error',
                message: e.message,
                stack: e.stack
            };
        }
    }
    
    /**
     * Test connection
     */
    function testConnection() {
        return {
            status: 'success',
            message: 'NetSuite connection successful',
            timestamp: new Date().toISOString()
        };
    }
    
    /**
     * Get sales transactions
     */
    function getSalesTransactions(params) {
        var startDate = params.start_date;
        var endDate = params.end_date;
        var filters = params.filters || {};
        
        var transactionSearch = search.create({
            type: search.Type.TRANSACTION,
            filters: [
                ['type', 'anyof', ['CustInvc', 'SalesOrd']],
                'AND',
                ['trandate', 'within', startDate, endDate],
                'AND',
                ['mainline', 'is', 'F'],
                'AND',
                ['taxline', 'is', 'F']
            ],
            columns: [
                search.createColumn({ name: 'internalid', label: 'transaction_id' }),
                search.createColumn({ name: 'trandate', label: 'transaction_date' }),
                search.createColumn({ name: 'type', label: 'transaction_type' }),
                search.createColumn({ name: 'entity', label: 'customer_id' }),
                search.createColumn({ name: 'item', label: 'item_id' }),
                search.createColumn({ name: 'quantity', label: 'sales_units' }),
                search.createColumn({ name: 'amount', label: 'sales_dollars' }),
                search.createColumn({ name: 'quantityreturned', label: 'returns' })
            ]
        });
        
        // Apply additional filters if provided
        if (filters.category && filters.category.length > 0) {
            transactionSearch.filters.push('AND');
            transactionSearch.filters.push(['item.class', 'anyof', filters.category]);
        }
        
        if (filters.vendor && filters.vendor.length > 0) {
            transactionSearch.filters.push('AND');
            transactionSearch.filters.push(['item.vendor', 'anyof', filters.vendor]);
        }
        
        if (filters.style) {
            transactionSearch.filters.push('AND');
            transactionSearch.filters.push(['item.custitem_style', 'is', filters.style]);
        }
        
        if (filters.customer) {
            transactionSearch.filters.push('AND');
            transactionSearch.filters.push(['entity', 'is', filters.customer]);
        }
        
        var results = [];
        var pagedData = transactionSearch.runPaged({ pageSize: 1000 });
        
        pagedData.pageRanges.forEach(function(pageRange) {
            var page = pagedData.fetch({ index: pageRange.index });
            page.data.forEach(function(result) {
                results.push({
                    transaction_id: result.getValue('internalid'),
                    transaction_date: result.getValue('trandate'),
                    transaction_type: result.getValue('type'),
                    customer_id: result.getValue('entity'),
                    item_id: result.getValue('item'),
                    sales_units: parseFloat(result.getValue('quantity')) || 0,
                    sales_dollars: parseFloat(result.getValue('amount')) || 0,
                    returns: parseFloat(result.getValue('quantityreturned')) || 0
                });
            });
        });
        
        return {
            status: 'success',
            data: results,
            count: results.length
        };
    }
    
    /**
     * Get item master data
     */
    function getItemMaster(params) {
        var itemIds = params.item_ids || [];
        
        var itemSearch = search.create({
            type: search.Type.ITEM,
            filters: itemIds.length > 0 ? 
                [['internalid', 'anyof', itemIds]] : 
                [],
            columns: [
                search.createColumn({ name: 'internalid', label: 'item_id' }),
                search.createColumn({ name: 'itemid', label: 'item_name' }),
                search.createColumn({ name: 'custitem_style', label: 'style' }),
                search.createColumn({ name: 'custitem_material_desc', label: 'material_desc' }),
                search.createColumn({ name: 'custitem_color_desc', label: 'color_desc' }),
                search.createColumn({ name: 'class', label: 'category' }),
                search.createColumn({ name: 'vendor', label: 'vendor' }),
                search.createColumn({ name: 'baseprice', label: 'retail_price' })
            ]
        });
        
        var results = [];
        itemSearch.run().each(function(result) {
            results.push({
                item_id: result.getValue('internalid'),
                item_name: result.getValue('itemid'),
                style: result.getValue('custitem_style'),
                material_desc: result.getValue('custitem_material_desc'),
                color_desc: result.getValue('custitem_color_desc'),
                category: result.getText('class'),
                vendor: result.getText('vendor'),
                retail_price: parseFloat(result.getValue('baseprice')) || 0
            });
            return true;
        });
        
        return {
            status: 'success',
            data: results,
            count: results.length
        };
    }
    
    /**
     * Get customer master data
     */
    function getCustomerMaster(params) {
        var customerIds = params.customer_ids || [];
        
        var customerSearch = search.create({
            type: search.Type.CUSTOMER,
            filters: customerIds.length > 0 ? 
                [['internalid', 'anyof', customerIds]] : 
                [],
            columns: [
                search.createColumn({ name: 'internalid', label: 'customer_id' }),
                search.createColumn({ name: 'entityid', label: 'customer' }),
                search.createColumn({ name: 'custentity_territory', label: 'territory' }),
                search.createColumn({ name: 'category', label: 'customer_category' })
            ]
        });
        
        var results = [];
        customerSearch.run().each(function(result) {
            results.push({
                customer_id: result.getValue('internalid'),
                customer: result.getValue('entityid'),
                territory: result.getText('custentity_territory'),
                customer_category: result.getText('category')
            });
            return true;
        });
        
        return {
            status: 'success',
            data: results,
            count: results.length
        };
    }
    
    /**
     * Execute saved search
     */
    function executeSavedSearch(params) {
        var searchId = params.search_id;
        var filters = params.filters || {};
        
        var savedSearch = search.load({ id: searchId });
        
        // Apply runtime filters if provided
        // (Implementation depends on specific search requirements)
        
        var results = [];
        savedSearch.run().each(function(result) {
            var row = {};
            result.columns.forEach(function(column) {
                row[column.label || column.name] = result.getValue(column);
            });
            results.push(row);
            return true;
        });
        
        return {
            status: 'success',
            data: results,
            count: results.length
        };
    }
    
    /**
     * Get corrected cost/retail data
     * This should pull from the Merchandising-maintained cost/retail file
     * 
     * NOTE: This is a placeholder. The actual implementation will depend on
     * how Annie maintains the cost/retail master (custom record, CSV import, etc.)
     */
    function getCostRetailData(params) {
        var itemIds = params.item_ids || [];
        
        // TODO: Replace with actual custom record or file lookup
        // This is a placeholder that returns NetSuite's base price
        // In production, this should pull from Annie's cost/retail master
        
        var itemSearch = search.create({
            type: search.Type.ITEM,
            filters: itemIds.length > 0 ? 
                [['internalid', 'anyof', itemIds]] : 
                [],
            columns: [
                search.createColumn({ name: 'internalid' }),
                search.createColumn({ name: 'custitem_corrected_cost' }), // Custom field
                search.createColumn({ name: 'baseprice' })
            ]
        });
        
        var costData = {};
        itemSearch.run().each(function(result) {
            var itemId = result.getValue('internalid');
            costData[itemId] = {
                cost: parseFloat(result.getValue('custitem_corrected_cost')) || 0,
                retail: parseFloat(result.getValue('baseprice')) || 0
            };
            return true;
        });
        
        return {
            status: 'success',
            data: costData
        };
    }
    
    return {
        post: post
    };
});
